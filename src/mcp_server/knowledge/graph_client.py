"""Knowledge graph client using NetworkX with JSON file loading"""

import json
import networkx as nx
from pathlib import Path
from typing import Optional, Dict, Any, List


class GraphClient:
    """Knowledge graph client for master investment knowledge"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the graph client.

        Args:
            db_path: Base path for knowledge files (default: data/knowledge/graph/)
        """
        self.graph = nx.DiGraph()
        self.db_path = Path(db_path) if db_path else Path("data/knowledge/graph")
        self._load_from_json()

    def _load_from_json(self):
        """Load knowledge from JSON files"""
        # Load masters
        masters_dir = self.db_path / "masters"
        if masters_dir.exists():
            for f in masters_dir.glob("*.json"):
                self._load_master(f)

        # Load concepts
        concepts_dir = self.db_path / "concepts"
        if concepts_dir.exists():
            for f in concepts_dir.glob("*.json"):
                self._load_concept(f)

        # Load relationships
        relations_file = self.db_path / "relations" / "relationships.json"
        if relations_file.exists():
            self._load_relations(relations_file)

    def _load_master(self, filepath: Path):
        """Load a master node from JSON"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        node_id = data.get("id")
        if node_id:
            self.graph.add_node(node_id, type="InvestmentMaster", **data)

    def _load_concept(self, filepath: Path):
        """Load a concept node from JSON"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        node_id = data.get("id")
        if node_id:
            self.graph.add_node(node_id, type="InvestmentConcept", **data)

    def _load_relations(self, filepath: Path):
        """Load relationships from JSON"""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for rel in data.get("relationships", []):
            self.graph.add_edge(
                rel["source"],
                rel["target"],
                relation=rel.get("type"),
                description=rel.get("description", "")
            )

    def query(self, node_type: Optional[str] = None, name: Optional[str] = None) -> list:
        """Query nodes from the graph"""
        results = []
        for node, data in self.graph.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            if name:
                name_lower = name.lower()
                in_id = name_lower in node.lower()
                in_name = name_lower in data.get("name", "").lower()
                in_name_en = name_lower in data.get("name_en", "").lower()
                if not (in_id or in_name or in_name_en):
                    continue
            results.append({"id": node, **data})
        return results

    def get_related(self, node: str, relation_type: Optional[str] = None) -> list:
        """Get nodes related to a given node"""
        results = []
        for neighbor in self.graph.neighbors(node):
            edge_data = self.graph.get_edge_data(node, neighbor)
            if relation_type and edge_data.get("relation") != relation_type:
                continue
            results.append({
                "id": neighbor,
                "relation": edge_data.get("relation"),
                "description": edge_data.get("description", ""),
                **self.graph.nodes[neighbor]
            })
        return results

    def get_master_by_id(self, master_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific master by ID"""
        if master_id in self.graph.nodes:
            data = self.graph.nodes[master_id]
            if data.get("type") == "InvestmentMaster":
                return {"id": master_id, **data}
        return None

    def get_concept_by_id(self, concept_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific concept by ID"""
        if concept_id in self.graph.nodes:
            data = self.graph.nodes[concept_id]
            if data.get("type") == "InvestmentConcept":
                return {"id": concept_id, **data}
        return None

    def find_concepts_by_keyword(self, keyword: str) -> list:
        """Find concepts matching a keyword in name or definition"""
        keyword_lower = keyword.lower()
        results = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") != "InvestmentConcept":
                continue
            name = data.get("name", "").lower()
            definition = data.get("definition", "").lower()
            if keyword_lower in name or keyword_lower in definition:
                results.append({"id": node, **data})
        return results

    def find_masters_by_keyword(self, keyword: str) -> list:
        """Find masters matching a keyword"""
        keyword_lower = keyword.lower()
        results = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") != "InvestmentMaster":
                continue
            name = data.get("name", "").lower()
            methodology = data.get("methodology", "").lower()
            if keyword_lower in name or keyword_lower in methodology:
                results.append({"id": node, **data})
        return results


# Singleton instance
_graph_client: Optional[GraphClient] = None


def get_graph_client() -> GraphClient:
    """Get the singleton graph client instance"""
    global _graph_client
    if _graph_client is None:
        _graph_client = GraphClient()
    return _graph_client