from typing import List, Optional
import numpy as np


class EmbeddingService:
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self.model_name = model_name
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
        except ImportError:
            raise ImportError("请安装 sentence-transformers: pip install sentence-transformers")
        except Exception as e:
            raise RuntimeError(f"无法加载嵌入模型 {self.model_name}: {e}")

    def encode(self, texts: List[str], normalize: bool = True) -> List[List[float]]:
        """将文本列表编码为向量"""
        if not texts:
            return []
        
        if self.model is None:
            self._initialize_model()
        
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=normalize)
        return embeddings.tolist()

    def encode_single(self, text: str, normalize: bool = True) -> List[float]:
        """编码单个文本"""
        return self.encode([text], normalize=normalize)[0]

    def similarity(self, a: List[float], b: List[float]) -> float:
        """计算两个向量的余弦相似度（假设向量已归一化）"""
        if not a or not b or len(a) != len(b):
            return 0.0
        
        a_arr = np.array(a)
        b_arr = np.array(b)
        
        return float(np.dot(a_arr, b_arr))
