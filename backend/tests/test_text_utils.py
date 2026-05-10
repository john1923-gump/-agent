"""text_utils模块的单元测试。"""
import pytest
from app.utils.text_utils import gen_id, clean_text, split_chunks, truncate


class TestGenId:
    """gen_id函数测试。"""

    def test_gen_id_returns_string(self):
        """测试gen_id返回字符串。"""
        result = gen_id()
        assert isinstance(result, str)

    def test_gen_id_length(self):
        """测试gen_id返回12位字符串。"""
        result = gen_id()
        assert len(result) == 12

    def test_gen_id_unique(self):
        """测试gen_id生成的ID不重复。"""
        ids = [gen_id() for _ in range(100)]
        assert len(set(ids)) == 100


class TestCleanText:
    """clean_text函数测试。"""

    def test_clean_text_removes_extra_whitespace(self):
        """测试清理多余空白字符。"""
        text = "  hello   world  \n\t  test  "
        result = clean_text(text)
        assert result == "hello world test"

    def test_clean_text_preserves_single_spaces(self):
        """测试保留单词间单个空格。"""
        text = "hello world"
        result = clean_text(text)
        assert result == "hello world"

    def test_clean_text_empty_string(self):
        """测试空字符串。"""
        result = clean_text("")
        assert result == ""


class TestSplitChunks:
    """split_chunks函数测试。"""

    def test_split_chunks_short_text(self):
        """测试短文本不分割。"""
        text = "short text"
        result = split_chunks(text, chunk_size=100, overlap=20)
        assert len(result) == 1
        assert result[0] == "short text"

    def test_split_chunks_long_text(self):
        """测试长文本正确分割。"""
        text = "a" * 1000
        result = split_chunks(text, chunk_size=300, overlap=50)
        assert len(result) > 1
        # 验证每个chunk不超过chunk_size
        for chunk in result:
            assert len(chunk) <= 300

    def test_split_chunks_overlap(self):
        """测试重叠区域正确。"""
        text = "abcdefghij" * 20  # 200字符
        result = split_chunks(text, chunk_size=100, overlap=20)
        if len(result) > 1:
            # 验证重叠：第一个chunk的末尾应该出现在第二个chunk的开头
            first_end = result[0][-20:]
            second_start = result[1][:20]
            assert first_end == second_start

    def test_split_chunks_empty_text(self):
        """测试空文本。"""
        result = split_chunks("", chunk_size=100, overlap=20)
        assert result == []

    def test_split_chunks_whitespace_only(self):
        """测试纯空白文本。"""
        result = split_chunks("   \n\t  ", chunk_size=100, overlap=20)
        assert result == []

    def test_split_chunks_default_params(self):
        """测试默认参数。"""
        text = "x" * 2000
        result = split_chunks(text)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 600


class TestTruncate:
    """truncate函数测试。"""

    def test_truncate_short_text(self):
        """测试短文本不截断。"""
        text = "short"
        result = truncate(text, max_len=100)
        assert result == "short"

    def test_truncate_long_text(self):
        """测试长文本截断并添加省略号。"""
        text = "a" * 200
        result = truncate(text, max_len=50)
        assert len(result) == 53  # 50 + "..."
        assert result.endswith("...")

    def test_truncate_exact_length(self):
        """测试正好等于max_len的文本。"""
        text = "x" * 100
        result = truncate(text, max_len=100)
        assert result == text

    def test_truncate_default_max_len(self):
        """测试默认max_len参数。"""
        text = "x" * 300
        result = truncate(text)
        assert len(result) == 203  # 200 + "..."
