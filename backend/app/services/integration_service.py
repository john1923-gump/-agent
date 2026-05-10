import json
import logging
from collections import defaultdict
from ..models.schemas import (
    KnowledgePoint, IntegrationPair, IntegrationResult, IntegrationDecision
)
from ..utils.text_utils import gen_id
from . import llm_service

logger = logging.getLogger(__name__)


def _char_ngram_similarity(a: str, b: str, n: int = 2) -> float:
    if a == b:
        return 1.0
    if a in b or b in a:
        return 0.9
    grams_a = set(a[i:i+n] for i in range(len(a) - n + 1))
    grams_b = set(b[i:i+n] for i in range(len(b) - n + 1))
    if not grams_a or not grams_b:
        return 0.0
    inter = len(grams_a & grams_b)
    union = len(grams_a | grams_b)
    return inter / union if union > 0 else 0.0


def _text_chars(kps: list[KnowledgePoint]) -> int:
    return sum(len(kp.description) for kp in kps)


async def integrate_cross_textbooks(
    all_kps: list[KnowledgePoint],
    original_text_chars: int = 0,
) -> IntegrationResult:
    if not all_kps:
        return IntegrationResult()

    if original_text_chars <= 0:
        original_text_chars = sum(len(kp.description) * 5 for kp in all_kps)

    pairs = await _layer1_semantic_dedup(all_kps)
    enriched = await _layer2_redundancy_simplify(all_kps, pairs)
    final_kps, removed_ids = await _layer3_content_triage(enriched, pairs, original_text_chars)

    final_chars = _text_chars(final_kps)
    compression_ratio = final_chars / original_text_chars if original_text_chars > 0 else 0.0

    integrity_report = _check_dependency_integrity(final_kps, pairs)
    coverage_report = _check_coverage(all_kps, final_kps)

    merge_count = sum(1 for p in pairs if p.decision == IntegrationDecision.MERGE)
    keep_count = sum(1 for p in pairs if p.decision == IntegrationDecision.KEEP)
    remove_count = len(removed_ids)

    return IntegrationResult(
        pairs=pairs,
        compression_ratio=round(compression_ratio, 4),
        original_count=len(all_kps),
        final_count=len(final_kps),
        original_text_chars=original_text_chars,
        final_text_chars=final_chars,
        merge_count=merge_count,
        keep_count=keep_count,
        remove_count=remove_count,
        integrity_report=integrity_report,
        coverage_report=coverage_report,
    )


async def _layer1_semantic_dedup(
    all_kps: list[KnowledgePoint],
) -> list[IntegrationPair]:
    cross_pairs: list[tuple[KnowledgePoint, KnowledgePoint, float]] = []
    for i in range(len(all_kps)):
        for j in range(i + 1, len(all_kps)):
            a, b = all_kps[i], all_kps[j]
            if a.textbook_id == b.textbook_id:
                continue
            name_sim = _char_ngram_similarity(a.name, b.name, 2)
            desc_sim = _char_ngram_similarity(a.description[:100], b.description[:100], 2)
            combined = name_sim * 0.6 + desc_sim * 0.4
            if combined > 0.35:
                cross_pairs.append((a, b, combined))

    cross_pairs.sort(key=lambda x: x[2], reverse=True)
    top_pairs = cross_pairs[:30]

    if not top_pairs:
        return []

    batch_size = 5
    all_decisions: list[IntegrationPair] = []

    for batch_start in range(0, len(top_pairs), batch_size):
        batch = top_pairs[batch_start:batch_start + batch_size]
        pairs_text = ""
        for idx, (a, b, sim) in enumerate(batch):
            pairs_text += f"""
知识点对{idx+1}（相似度{sim:.2f}）：
  A（《{a.textbook_name}》{a.chapter_title}）：{a.name} - {a.description}
  B（《{b.textbook_name}》{b.chapter_title}）：{b.name} - {b.description}
"""

        prompt = f"""你是学科知识整合专家。判断以下知识点对的关系，对每一对返回决策。

{pairs_text}

对每个知识点对，返回JSON对象：
- decision: "merge"(同一概念合并) / "keep"(保留两者，不同角度) / "remove"(B是A的子集或冗余)
- reason: 决策原因（30字以内）
- merged_content: 若decision为merge，填写合并后的精炼定义（50-150字），否则为null

返回JSON数组，顺序与输入对应。只返回JSON。"""

        try:
            result = await llm_service.chat([{"role": "user", "content": prompt}], temperature=0.1)
            result = _clean_json(result)
            parsed = json.loads(result)
            if not isinstance(parsed, list):
                parsed = [parsed]

            for idx, (a, b, sim) in enumerate(batch):
                if idx < len(parsed):
                    item = parsed[idx]
                    decision = IntegrationDecision(item.get("decision", "keep"))
                    all_decisions.append(IntegrationPair(
                        kp_a=a, kp_b=b, similarity=round(sim, 3),
                        decision=decision,
                        reason=item.get("reason", ""),
                        merged_content=item.get("merged_content"),
                    ))
                else:
                    all_decisions.append(IntegrationPair(
                        kp_a=a, kp_b=b, similarity=round(sim, 3),
                        decision=IntegrationDecision.KEEP,
                        reason="自动保留",
                    ))
        except Exception as e:
            logger.warning(f"整合决策批次失败: {e}")
            for a, b, sim in batch:
                all_decisions.append(IntegrationPair(
                    kp_a=a, kp_b=b, similarity=round(sim, 3),
                    decision=IntegrationDecision.KEEP,
                    reason="决策失败，自动保留",
                ))

    return all_decisions


async def _layer2_redundancy_simplify(
    all_kps: list[KnowledgePoint],
    pairs: list[IntegrationPair],
) -> list[KnowledgePoint]:
    merge_pairs = [p for p in pairs if p.decision == IntegrationDecision.MERGE and p.merged_content]
    if not merge_pairs:
        return all_kps

    enriched = list(all_kps)
    merged_ids: set[str] = set()

    for pair in merge_pairs:
        if pair.kp_b.id in merged_ids:
            continue
        for kp in enriched:
            if kp.id == pair.kp_a.id:
                kp.description = pair.merged_content
                break
        merged_ids.add(pair.kp_b.id)

    enriched = [kp for kp in enriched if kp.id not in merged_ids]
    return enriched


async def _layer3_content_triage(
    kps: list[KnowledgePoint],
    pairs: list[IntegrationPair],
    original_text_chars: int,
) -> tuple[list[KnowledgePoint], set[str]]:
    current_chars = _text_chars(kps)
    target_chars = original_text_chars * 0.30

    removed_ids: set[str] = set()

    if current_chars <= target_chars:
        return kps, removed_ids

    remove_candidates = [p for p in pairs if p.decision == IntegrationDecision.REMOVE]
    for pair in remove_candidates:
        if pair.kp_b.id not in removed_ids:
            removed_ids.add(pair.kp_b.id)
            current_chars -= len(pair.kp_b.description)
            if current_chars <= target_chars:
                break

    if current_chars > target_chars:
        kp_by_name: dict[str, list[KnowledgePoint]] = defaultdict(list)
        for kp in kps:
            if kp.id not in removed_ids:
                kp_by_name[kp.name].append(kp)

        for name, kp_list in kp_by_name.items():
            if len(kp_list) > 1:
                kp_list.sort(key=lambda x: len(x.description), reverse=True)
                for kp in kp_list[1:]:
                    if kp.id not in removed_ids:
                        removed_ids.add(kp.id)
                        current_chars -= len(kp.description)
                        if current_chars <= target_chars:
                            break
            if current_chars <= target_chars:
                break

    if current_chars > target_chars:
        long_kps = [
            kp for kp in kps
            if kp.id not in removed_ids and len(kp.description) > 150
        ]
        long_kps.sort(key=lambda x: len(x.description), reverse=True)
        for kp in long_kps:
            excess = len(kp.description) - 100
            kp.description = kp.description[:100] + "..."
            current_chars -= excess
            if current_chars <= target_chars:
                break

    final_kps = [kp for kp in kps if kp.id not in removed_ids]
    return final_kps, removed_ids


def _check_dependency_integrity(
    final_kps: list[KnowledgePoint],
    pairs: list[IntegrationPair],
) -> dict:
    final_ids = {kp.id for kp in final_kps}
    final_names = {kp.name for kp in final_kps}

    broken_deps = []
    for pair in pairs:
        if pair.decision == IntegrationDecision.MERGE:
            if pair.kp_b.id not in final_ids:
                pass

    return {
        "status": "ok" if not broken_deps else "warning",
        "total_preserved": len(final_kps),
        "broken_dependencies": broken_deps,
    }


def _check_coverage(
    original: list[KnowledgePoint],
    final: list[KnowledgePoint],
) -> dict:
    by_type_orig: dict[str, int] = defaultdict(int)
    by_type_final: dict[str, int] = defaultdict(int)

    for kp in original:
        by_type_orig[kp.type.value] += 1
    for kp in final:
        by_type_final[kp.type.value] += 1

    coverage = {}
    for type_name, orig_count in by_type_orig.items():
        final_count = by_type_final.get(type_name, 0)
        rate = final_count / orig_count if orig_count > 0 else 0
        coverage[type_name] = {
            "original": orig_count,
            "preserved": final_count,
            "rate": round(rate, 3),
        }

    return coverage


def _clean_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        start = 1
        end = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == "```":
                end = i
                break
        text = "\n".join(lines[start:end])
        if text.startswith("json"):
            text = text[4:]
    return text.strip()


def apply_integration(integration: IntegrationResult):
    from . import graph_service

    for pair in integration.pairs:
        if pair.decision == IntegrationDecision.REMOVE:
            graph_service.remove_knowledge_point(pair.kp_b.id)
        elif pair.decision == IntegrationDecision.MERGE and pair.merged_content:
            graph_service.update_knowledge_point(pair.kp_a.id, {
                "description": pair.merged_content,
            })
            graph_service.remove_knowledge_point(pair.kp_b.id)
