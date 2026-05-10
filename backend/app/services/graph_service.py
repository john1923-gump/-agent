"""知识图谱服务：管理知识点和图谱的CRUD操作。"""
import logging
from ..models.schemas import (
    KnowledgePoint, KnowledgeGraph, GraphNode, GraphEdge, KnowledgeType, Chapter
)
from ..utils.text_utils import gen_id
from . import llm_service

logger = logging.getLogger(__name__)

knowledge_points_db: dict[str, KnowledgePoint] = {}
knowledge_graph = KnowledgeGraph()
_raw_relationships: list[dict] = []


async def extract_and_build(chapters: list[Chapter]) -> list[KnowledgePoint]:
    """从章节列表中提取知识点并构建知识图谱。

    Args:
        chapters: 章节列表，每个章节包含标题和内容。

    Returns:
        提取的知识点列表。
    """
    all_kps: list[KnowledgePoint] = []
    all_rels: list[dict] = []

    for ch in chapters:
        result = await llm_service.extract_knowledge_points(ch.content, ch.title)
        raw_list = result.get("knowledge_points", [])
        rels = result.get("relationships", [])

        for raw in raw_list:
            kp_type = KnowledgeType.CONCEPT
            for t in KnowledgeType:
                if t.value == raw.get("type", ""):
                    kp_type = t
                    break
            kp = KnowledgePoint(
                id=gen_id(),
                chapter_id=ch.id,
                textbook_id=ch.textbook_id,
                textbook_name=ch.textbook_name,
                chapter_title=ch.title,
                name=raw.get("name", "未知"),
                description=raw.get("description", ""),
                type=kp_type,
            )
            knowledge_points_db[kp.id] = kp
            all_kps.append(kp)

        all_rels.extend(rels)

    global _raw_relationships
    _raw_relationships = all_rels
    _rebuild_graph()
    return all_kps


def _rebuild_graph() -> None:
    """重建知识图谱，生成节点和边。"""
    name_to_ids: dict[str, list[str]] = {}
    name_to_desc: dict[str, str] = {}
    name_to_chapter: dict[str, str] = {}
    for kp in knowledge_points_db.values():
        name_to_ids.setdefault(kp.name, []).append(kp.id)
        name_to_desc[kp.name] = kp.description
        name_to_chapter[kp.name] = kp.chapter_title

    nodes = []
    seen_names: set[str] = set()

    for name, ids in name_to_ids.items():
        rep_id = ids[0]
        rep_kp = knowledge_points_db[rep_id]
        node = GraphNode(
            id=rep_id,
            label=name,
            type=rep_kp.type,
            textbook_id=rep_kp.textbook_id,
            textbook_name=rep_kp.textbook_name,
            chapter_title=name_to_chapter.get(name, ""),
            description=name_to_desc.get(name, ""),
            frequency=len(ids),
            size=min(10 + len(ids) * 8, 60),
        )
        nodes.append(node)
        seen_names.add(name)

    edges = []
    edge_set: set[tuple[str, str]] = set()

    for rel in _raw_relationships:
        src_name = rel.get("source", "")
        tgt_name = rel.get("target", "")
        rel_type = rel.get("relation", "相关")
        if src_name in name_to_ids and tgt_name in name_to_ids:
            src_id = name_to_ids[src_name][0]
            tgt_id = name_to_ids[tgt_name][0]
            edge_key = (src_id, tgt_id)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                weight_map = {"prerequisite": 1.0, "contains": 0.8, "applies_to": 0.6, "parallel": 0.4}
                edges.append(GraphEdge(
                    source=src_id,
                    target=tgt_id,
                    relation=rel_type,
                    weight=weight_map.get(rel_type, 0.5),
                ))

    kp_list = list(knowledge_points_db.values())
    for i in range(len(kp_list)):
        for j in range(i + 1, len(kp_list)):
            a, b = kp_list[i], kp_list[j]
            if a.chapter_id == b.chapter_id:
                edge_key = (a.id, b.id)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append(GraphEdge(source=a.id, target=b.id, relation="同章节", weight=0.3))
            if a.name == b.name and a.textbook_id != b.textbook_id:
                edge_key = (a.id, b.id)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append(GraphEdge(source=a.id, target=b.id, relation="同概念", weight=1.0))

    knowledge_graph.nodes = nodes
    knowledge_graph.edges = edges


def get_graph() -> KnowledgeGraph:
    """获取当前知识图谱。

    Returns:
        知识图谱对象，包含节点和边。
    """
    return knowledge_graph


def get_all_knowledge_points() -> list[KnowledgePoint]:
    """获取所有知识点列表。

    Returns:
        知识点列表。
    """
    return list(knowledge_points_db.values())


def get_knowledge_point(kp_id: str) -> KnowledgePoint | None:
    """根据ID获取单个知识点。

    Args:
        kp_id: 知识点ID。

    Returns:
        知识点对象，不存在则返回None。
    """
    return knowledge_points_db.get(kp_id)


def add_knowledge_point(kp: KnowledgePoint) -> None:
    """添加知识点到数据库。

    Args:
        kp: 知识点对象。
    """
    knowledge_points_db[kp.id] = kp
    _rebuild_graph()


def remove_knowledge_point(kp_id: str) -> None:
    """从数据库中删除知识点。

    Args:
        kp_id: 要删除的知识点ID。
    """
    knowledge_points_db.pop(kp_id, None)
    _rebuild_graph()


def update_knowledge_point(kp_id: str, updates: dict) -> None:
    """更新知识点属性。

    Args:
        kp_id: 要更新的知识点ID。
        updates: 要更新的属性字典。
    """
    kp = knowledge_points_db.get(kp_id)
    if kp:
        for k, v in updates.items():
            if hasattr(kp, k):
                setattr(kp, k, v)
        _rebuild_graph()
