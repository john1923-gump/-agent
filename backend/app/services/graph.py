from typing import List
from app.models.knowledge import KnowledgeGraph, KnowledgeNode, KnowledgeEdge


class GraphService:
    """知识图谱构建与管理服务"""

    def __init__(self):
        self.current_graph: KnowledgeGraph = KnowledgeGraph(nodes=[], edges=[])

    def build_graph(self, nodes: List[KnowledgeNode], edges: List[KnowledgeEdge]) -> KnowledgeGraph:
        """从节点和边列表构建图"""
        self.current_graph = KnowledgeGraph(nodes=nodes, edges=edges, metadata={"generated_by": "GraphService"})
        return self.current_graph

    def add_nodes(self, nodes: List[KnowledgeNode]):
        """添加节点到当前图"""
        existing_ids = {n.id for n in self.current_graph.nodes}
        for node in nodes:
            if node.id not in existing_ids:
                self.current_graph.nodes.append(node)

    def add_edges(self, edges: List[KnowledgeEdge]):
        """添加边到当前图"""
        self.current_graph.edges.extend(edges)

    def merge_graphs(self, graphs: List[KnowledgeGraph]) -> KnowledgeGraph:
        """合并多个图为一个"""
        merged_nodes = []
        merged_edges = []
        node_id_map = {}

        # 合并节点，去重
        for graph in graphs:
            for node in graph.nodes:
                existing = next((n for n in merged_nodes if n.label == node.label), None)
                if existing:
                    existing.frequency += node.frequency
                    node_id_map[node.id] = existing.id
                else:
                    merged_nodes.append(node)
                    node_id_map[node.id] = node.id

        # 合并边，更新节点引用
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
                    new_edge = KnowledgeEdge(
                        id=edge.id, source=new_source, target=new_target, relation=edge.relation, weight=edge.weight
                    )
                    merged_edges.append(new_edge)

        compression_ratio = (
            len([g for g in graphs for _ in g.nodes]) / len(merged_nodes) if merged_nodes else 1.0
        )

        self.current_graph = KnowledgeGraph(
            nodes=merged_nodes,
            edges=merged_edges,
            metadata={"merged_count": len(graphs), "compression_ratio": compression_ratio},
        )
        return self.current_graph

    def get_node_by_id(self, node_id: str) -> KnowledgeNode | None:
        """根据ID获取节点"""
        return next((n for n in self.current_graph.nodes if n.id == node_id), None)

    def get_connected_nodes(self, node_id: str) -> List[KnowledgeNode]:
        """获取与指定节点相连的所有节点"""
        connected_ids = set()
        for edge in self.current_graph.edges:
            if edge.source == node_id:
                connected_ids.add(edge.target)
            elif edge.target == node_id:
                connected_ids.add(edge.source)

        return [n for n in self.current_graph.nodes if n.id in connected_ids]

    def get_graph(self) -> KnowledgeGraph:
        """获取当前图"""
        return self.current_graph
