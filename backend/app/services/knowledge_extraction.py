from typing import List, Optional
from uuid import uuid4
import json
from app.models.knowledge import KnowledgePoint, KnowledgeNode, KnowledgeEdge, KnowledgeGraph
from app.models.document import DocumentStructure, Section
from app.services.embedding import EmbeddingService


class KnowledgeExtractionService:
    """从教材章节提取知识点并构建知识图谱"""

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        self.embedding_service = embedding_service or EmbeddingService()
        self.knowledge_points: List[KnowledgePoint] = []
        self.nodes: List[KnowledgeNode] = []
        self.edges: List[KnowledgeEdge] = []

    def extract_from_document(self, document: DocumentStructure) -> List[KnowledgePoint]:
        """从文档结构提取知识点（简单启发式方法）"""
        knowledge_points = []
        
        for section in document.sections:
            # 简单的启发式提取：按行分割，识别关键模式
            lines = section.text.split("\n")
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 5:
                    continue
                
                # 识别定义和定理
                point_type = self._classify_point_type(line)
                if point_type:
                    kp = KnowledgePoint(
                        id=str(uuid4()),
                        title=line[:50],
                        type=point_type,
                        description=line,
                        source_document_id=document.source.id,
                        section_id=section.id,
                        tags=self._extract_tags(line),
                        frequency=1,
                    )
                    knowledge_points.append(kp)
        
        self.knowledge_points.extend(knowledge_points)
        return knowledge_points

    def _classify_point_type(self, text: str) -> Optional[str]:
        """分类知识点类型"""
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ["定义", "is defined as", "means", "即"]):
            return "概念"
        if any(kw in text_lower for kw in ["定理", "theorem", "法则", "law"]):
            return "定理"
        if any(kw in text_lower for kw in ["方法", "步骤", "步驟", "procedure", "method"]):
            return "方法"
        if any(kw in text_lower for kw in ["现象", "现象", "phenomenon", "occurs"]):
            return "现象"
        
        return None

    def _extract_tags(self, text: str) -> List[str]:
        """从文本中提取标签（关键词）"""
        # 简单关键词提取：按长度和位置选择
        words = text.split()
        tags = []
        
        for word in words[:5]:
            word = word.strip("，。；：、").strip()
            if len(word) > 2:
                tags.append(word)
        
        return tags[:3]

    def build_graph_from_knowledge_points(
        self, knowledge_points: List[KnowledgePoint]
    ) -> KnowledgeGraph:
        """基于知识点构建知识图谱"""
        self.nodes = []
        self.edges = []
        
        # 创建节点
        point_to_node = {}
        for kp in knowledge_points:
            node = KnowledgeNode(
                id=kp.id,
                label=kp.title,
                category=kp.type,
                description=kp.description,
                source=kp.source_document_id,
                frequency=kp.frequency,
                metadata={"tags": kp.tags},
            )
            self.nodes.append(node)
            point_to_node[kp.id] = node

        # 创建边（简单的基于相似性）
        for i, kp1 in enumerate(knowledge_points):
            for kp2 in knowledge_points[i + 1 :]:
                similarity = self._compute_similarity(kp1.title, kp2.title)
                
                if similarity > 0.3:
                    relation = "相关"
                    if kp1.type == kp2.type:
                        relation = "同类"
                    
                    edge = KnowledgeEdge(
                        id=str(uuid4()),
                        source=kp1.id,
                        target=kp2.id,
                        relation=relation,
                        weight=similarity,
                    )
                    self.edges.append(edge)
        
        return KnowledgeGraph(nodes=self.nodes, edges=self.edges, metadata={"point_count": len(knowledge_points)})

    def _compute_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度（基于嵌入）"""
        try:
            emb1 = self.embedding_service.encode_single(text1)
            emb2 = self.embedding_service.encode_single(text2)
            return self.embedding_service.similarity(emb1, emb2)
        except Exception:
            return 0.0

    def merge_graphs(
        self, graphs: List[KnowledgeGraph], merge_strategy: str = "union"
    ) -> KnowledgeGraph:
        """合并多个知识图谱"""
        merged_nodes = []
        merged_edges = []
        node_id_map = {}
        
        for graph in graphs:
            for node in graph.nodes:
                existing = next((n for n in merged_nodes if n.label == node.label), None)
                if existing:
                    existing.frequency += 1
                    node_id_map[node.id] = existing.id
                else:
                    merged_nodes.append(node)
                    node_id_map[node.id] = node.id
        
        for graph in graphs:
            for edge in graph.edges:
                new_source = node_id_map.get(edge.source, edge.source)
                new_target = node_id_map.get(edge.target, edge.target)
                
                existing_edge = next(
                    (e for e in merged_edges if e.source == new_source and e.target == new_target),
                    None,
                )
                if existing_edge:
                    existing_edge.weight = (existing_edge.weight or 0) + (edge.weight or 0)
                else:
                    edge.source = new_source
                    edge.target = new_target
                    merged_edges.append(edge)
        
        compression_ratio = len(merged_nodes) / sum(len(g.nodes) for g in graphs) if graphs else 1.0
        
        return KnowledgeGraph(
            nodes=merged_nodes,
            edges=merged_edges,
            metadata={
                "merged_graph_count": len(graphs),
                "compression_ratio": compression_ratio,
            },
        )
