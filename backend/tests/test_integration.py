"""integration_service模块的单元测试。"""
import pytest
from app.services.integration_service import (
    _char_ngram_similarity,
    _text_chars,
    _clean_json,
    _check_coverage,
)
from app.models.schemas import KnowledgePoint, KnowledgeType


class TestCharNgramSimilarity:
    """_char_ngram_similarity函数测试。"""

    def test_identical_strings(self):
        """测试完全相同的字符串。"""
        result = _char_ngram_similarity("hello", "hello")
        assert result == 1.0

    def test_substring_contained(self):
        """测试子串包含关系。"""
        result = _char_ngram_similarity("hello", "hello world")
        assert result == 0.9

    def test_similar_strings(self):
        """测试相似字符串。"""
        result = _char_ngram_similarity("knowledge", "knowledg")
        assert result > 0.7

    def test_different_strings(self):
        """测试完全不同的字符串。"""
        result = _char_ngram_similarity("abc", "xyz")
        assert result < 0.2

    def test_empty_strings(self):
        """测试空字符串。"""
        result = _char_ngram_similarity("", "hello")
        assert result == 0.0

    def test_custom_ngram(self):
        """测试自定义n-gram参数。"""
        result = _char_ngram_similarity("abcdef", "abcxyz", n=3)
        assert result > 0


class TestTextChars:
    """_text_chars函数测试。"""

    def test_single_kp(self):
        """测试单个知识点。"""
        kps = [
            KnowledgePoint(
                id="test1",
                name="概念A",
                description="这是描述" * 10,
                type=KnowledgeType.CONCEPT,
            )
        ]
        result = _text_chars(kps)
        assert result == len("这是描述" * 10)

    def test_multiple_kps(self):
        """测试多个知识点。"""
        kps = [
            KnowledgePoint(
                id="test1",
                name="概念A",
                description="短描述",
                type=KnowledgeType.CONCEPT,
            ),
            KnowledgePoint(
                id="test2",
                name="概念B",
                description="另一个描述",
                type=KnowledgeType.THEOREM,
            ),
        ]
        result = _text_chars(kps)
        assert result == len("短描述") + len("另一个描述")

    def test_empty_list(self):
        """测试空列表。"""
        result = _text_chars([])
        assert result == 0


class TestCleanJson:
    """_clean_json函数测试。"""

    def test_clean_json_with_code_block(self):
        """测试清理markdown代码块。"""
        text = '```json\n{"key": "value"}\n```'
        result = _clean_json(text)
        assert result == '{"key": "value"}'

    def test_clean_json_without_code_block(self):
        """测试无代码块的JSON。"""
        text = '{"key": "value"}'
        result = _clean_json(text)
        assert result == '{"key": "value"}'

    def test_clean_json_with_whitespace(self):
        """测试清理空白。"""
        text = '  \n```json\n[1, 2, 3]\n```\n  '
        result = _clean_json(text)
        assert result == '[1, 2, 3]'


class TestCheckCoverage:
    """_check_coverage函数测试。"""

    def test_full_coverage(self):
        """测试完整覆盖率。"""
        original = [
            KnowledgePoint(id="1", name="A", description="", type=KnowledgeType.CONCEPT),
            KnowledgePoint(id="2", name="B", description="", type=KnowledgeType.THEOREM),
        ]
        final = [
            KnowledgePoint(id="1", name="A", description="", type=KnowledgeType.CONCEPT),
            KnowledgePoint(id="2", name="B", description="", type=KnowledgeType.THEOREM),
        ]
        result = _check_coverage(original, final)
        assert result["概念"]["rate"] == 1.0
        assert result["定理"]["rate"] == 1.0

    def test_partial_coverage(self):
        """测试部分覆盖率。"""
        original = [
            KnowledgePoint(id="1", name="A", description="", type=KnowledgeType.CONCEPT),
            KnowledgePoint(id="2", name="B", description="", type=KnowledgeType.CONCEPT),
            KnowledgePoint(id="3", name="C", description="", type=KnowledgeType.CONCEPT),
        ]
        final = [
            KnowledgePoint(id="1", name="A", description="", type=KnowledgeType.CONCEPT),
        ]
        result = _check_coverage(original, final)
        assert result["概念"]["original"] == 3
        assert result["概念"]["preserved"] == 1
        assert abs(result["概念"]["rate"] - 0.333) < 0.01

    def test_empty_original(self):
        """测试原始列表为空。"""
        result = _check_coverage([], [])
        assert result == {}
