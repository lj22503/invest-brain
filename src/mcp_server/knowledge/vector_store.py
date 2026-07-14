"""Vector store using Chroma for semantic search over investment knowledge."""

import json
import uuid
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings

# Default persist directory for vectors
DEFAULT_PERSIST_DIR = str(Path(__file__).resolve().parents[3] / "data" / "knowledge" / "vectors")
_DATA_ROOT = Path(__file__).resolve().parents[3] / "data" / "knowledge" / "graph"
_INDUSTRY_ROOT = Path(__file__).resolve().parents[3] / "data" / "knowledge" / "industry"
_FRAMEWORK_ROOT = Path(__file__).resolve().parents[3] / "data" / "knowledge" / "frameworks"


class VectorStore:
    """Chroma-based vector store for investment knowledge."""

    def __init__(self, persist_dir: str = DEFAULT_PERSIST_DIR):
        """
        Initialize the vector store.

        Args:
            persist_dir: Directory to persist Chroma data.
        """
        self.persist_dir = persist_dir
        Path(persist_dir).mkdir(parents=True, exist_ok=True)

        self._client = chromadb.PersistentClient(path=persist_dir)
        self._collection_master = self._client.get_or_create_collection(
            name="masters", metadata={"description": "大师思想库"}
        )
        self._collection_concept = self._client.get_or_create_collection(
            name="concepts", metadata={"description": "投资概念库"}
        )
        self._collection_buffett = self._client.get_or_create_collection(
            name="buffett_refs", metadata={"description": "巴菲特投资体系详细参考文献"}
        )
        self._collection_industry = self._client.get_or_create_collection(
            name="industry", metadata={"description": "行业研究框架"}
        )
        self._collection_framework = self._client.get_or_create_collection(
            name="frameworks", metadata={"description": "投资分析框架"}
        )
        self._collection_memories = self._client.get_or_create_collection(
            name="memories", metadata={"description": "用户投资想法记忆"}
        )

    def _textify_master(self, master_id: str) -> tuple[str, dict]:
        """Load a master JSON and extract text + metadata."""
        path = _DATA_ROOT / "masters" / f"{master_id}.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        parts = [
            data.get("name", ""),
            " ".join(data.get("core_principles", [])),
            data.get("methodology", ""),
            " ".join(f'"{q}"' for q in data.get("quotes", [])),
        ]
        text = " | ".join(p for p in parts if p)
        meta = {
            "type": "master",
            "id": data["id"],
            "name": data.get("name", ""),
            "name_en": data.get("name_en", ""),
            "era": data.get("era", ""),
        }
        return text, meta

    def _textify_concept(self, concept_id: str) -> tuple[str, dict]:
        """Load a concept JSON and extract text + metadata."""
        path = _DATA_ROOT / "concepts" / f"{concept_id}.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        parts = [
            data.get("name", ""),
            data.get("definition", ""),
            " ".join(f"例如：{e}" for e in data.get("examples", [])),
        ]
        text = " | ".join(p for p in parts if p)
        meta = {
            "type": "concept",
            "id": data["id"],
            "name": data.get("name", ""),
        }
        return text, meta

    def add_master(self, master_id: str, text: Optional[str] = None, metadata: Optional[dict] = None):
        """
        Add a master document to the store.

        Args:
            master_id: ID of the master (filename without .json).
            text: Optional override text; if None, extracted from JSON.
            metadata: Optional override metadata; if None, extracted from JSON.
        """
        if text is None or metadata is None:
            text, meta = self._textify_master(master_id)
            metadata = meta if metadata is None else metadata
        else:
            meta = {"type": "master", "id": master_id, **(metadata or {})}

        self._collection_master.upsert(
            ids=[master_id],
            documents=[text],
            metadatas=[meta],
        )

    def add_concept(self, concept_id: str, text: Optional[str] = None, metadata: Optional[dict] = None):
        """
        Add a concept document to the store.

        Args:
            concept_id: ID of the concept (filename without .json).
            text: Optional override text; if None, extracted from JSON.
            metadata: Optional override metadata; if None, extracted from JSON.
        """
        if text is None or metadata is None:
            text, meta = self._textify_concept(concept_id)
            metadata = meta if metadata is None else metadata
        else:
            meta = {"type": "concept", "id": concept_id, **(metadata or {})}

        self._collection_concept.upsert(
            ids=[concept_id],
            documents=[text],
            metadatas=[meta],
        )

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search across all knowledge.

        Args:
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of result dicts with keys: id, text, metadata, distance.
        """
        results = []
        # Search masters
        master_count = max(1, self._collection_master.count())
        master_results = self._collection_master.query(
            query_texts=[query], n_results=min(top_k, master_count)
        )
        for i in range(len(master_results["ids"][0])):
            results.append({
                "id": master_results["ids"][0][i],
                "text": master_results["documents"][0][i],
                "metadata": master_results["metadatas"][0][i],
                "distance": master_results["distances"][0][i],
            })
        # Search concepts
        concept_count = max(1, self._collection_concept.count())
        concept_results = self._collection_concept.query(
            query_texts=[query], n_results=min(top_k, concept_count)
        )
        for i in range(len(concept_results["ids"][0])):
            results.append({
                "id": concept_results["ids"][0][i],
                "text": concept_results["documents"][0][i],
                "metadata": concept_results["metadatas"][0][i],
                "distance": concept_results["distances"][0][i],
            })
        # Search industry
        industry_count = max(1, self._collection_industry.count())
        industry_results = self._collection_industry.query(
            query_texts=[query], n_results=min(top_k, industry_count)
        )
        for i in range(len(industry_results["ids"][0])):
            results.append({
                "id": industry_results["ids"][0][i],
                "text": industry_results["documents"][0][i],
                "metadata": industry_results["metadatas"][0][i],
                "distance": industry_results["distances"][0][i],
            })
        # Search frameworks
        framework_count = max(1, self._collection_framework.count())
        framework_results = self._collection_framework.query(
            query_texts=[query], n_results=min(top_k, framework_count)
        )
        for i in range(len(framework_results["ids"][0])):
            results.append({
                "id": framework_results["ids"][0][i],
                "text": framework_results["documents"][0][i],
                "metadata": framework_results["metadatas"][0][i],
                "distance": framework_results["distances"][0][i],
            })
        # Sort by distance
        results.sort(key=lambda x: x["distance"])
        return results[:top_k]

    def search_by_master(self, master_id: str, query: str, top_k: int = 3) -> list[dict]:
        """
        Semantic search filtered to a specific master.

        Args:
            master_id: ID of the master to search within.
            query: Search query string.
            top_k: Number of results to return.

        Returns:
            List of result dicts (concepts related to the master's thinking).
        """
        # First find concepts most similar to the master's own text
        master_text, _ = self._textify_master(master_id)

        # Search concepts and filter by relevance to master's thinking
        concept_count = max(1, self._collection_concept.count())
        concept_results = self._collection_concept.query(
            query_texts=[query], n_results=min(top_k *2, concept_count)
        )

        # Cross-reference with master's core principles
        master_path = Path("data/knowledge/graph/masters") / f"{master_id}.json"
        with open(master_path, encoding="utf-8") as f:
            master_data = json.load(f)
        master_principles = set(master_data.get("core_principles", []))

        filtered = []
        for i in range(len(concept_results["ids"][0])):
            concept_id = concept_results["ids"][0][i]
            concept_path = Path("data/knowledge/graph/concepts") / f"{concept_id}.json"
            if concept_path.exists():
                with open(concept_path, encoding="utf-8") as f:
                    concept_data = json.load(f)
                concept_name = concept_data.get("name", "")
                # Boost if concept is one of the master's core principles
                boost = 1.0 if concept_name in master_principles else 0.0
                distance = concept_results["distances"][0][i] - boost * 0.1
                filtered.append({
                    "id": concept_id,
                    "text": concept_results["documents"][0][i],
                    "metadata": concept_results["metadatas"][0][i],
                    "distance": distance,
                })

        filtered.sort(key=lambda x: x["distance"])
        return filtered[:top_k]

    def add_buffett_ref(self, filename: str):
        """Add a buffett reference markdown file to the store."""
        path = _DATA_ROOT / "masters" / "buffett-references" / filename
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Extract title from first line (## or # heading)
        lines = content.split("\n")
        title = lines[0].lstrip("# ").strip() if lines else filename

        meta = {
            "type": "buffett_ref",
            "id": filename,
            "title": title,
        }
        self._collection_buffett.upsert(
            ids=[filename],
            documents=[content],
            metadatas=[meta],
        )

    def add_industry_doc(self, filename: str):
        """Add an industry framework document to the store."""
        path = _INDUSTRY_ROOT / filename
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Extract title from first heading
        lines = content.split("\n")
        title = ""
        for line in lines[:10]:
            if line.startswith("#"):
                title = line.lstrip("# ").strip()
                break

        doc_id = path.stem  # filename without extension
        meta = {
            "type": "industry",
            "id": doc_id,
            "filename": filename,
            "title": title or doc_id,
        }
        self._collection_industry.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[meta],
        )

    def add_framework_doc(self, filename: str):
        """Add a framework document to the store."""
        path = _FRAMEWORK_ROOT / filename
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            content = f.read()

        # Extract title from first heading
        lines = content.split("\n")
        title = ""
        for line in lines[:10]:
            if line.startswith("#"):
                title = line.lstrip("# ").strip()
                break

        doc_id = path.stem
        meta = {
            "type": "framework",
            "id": doc_id,
            "filename": filename,
            "title": title or doc_id,
        }
        self._collection_framework.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[meta],
        )

    def add_memory(self, memory_id: str, text: str, metadata: dict = None):
        """Add a thought/memory to the memories collection."""
        meta = {
            "type": "thought",
            "id": memory_id,
            **(metadata or {}),
        }
        self._collection_memories.upsert(
            ids=[memory_id],
            documents=[text],
            metadatas=[meta],
        )

    def search_memories(self, query: str, top_k: int = 10) -> list[dict]:
        """
        Semantic search over user memories/thoughts.

        Args:
            query: Search query string.
            top_k: Number of results.

        Returns:
            List of dicts: {id, text, metadata, distance}
        """
        count = self._collection_memories.count()
        if count == 0:
            return []
        n = min(top_k, count)
        results = self._collection_memories.query(query_texts=[query], n_results=n)
        out = []
        for i in range(len(results["ids"][0])):
            out.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return out

    def rebuild_index(self):
        """Rebuild the index from all existing sources."""
        masters_dir = _DATA_ROOT / "masters"
        concepts_dir = _DATA_ROOT / "concepts"
        buffett_dir = _DATA_ROOT / "masters" / "buffett-references"

        for mf in masters_dir.glob("*.json"):
            master_id = mf.stem
            self.add_master(master_id)

        for cf in concepts_dir.glob("*.json"):
            concept_id = cf.stem
            self.add_concept(concept_id)

        for bf in buffett_dir.glob("*.md"):
            self.add_buffett_ref(bf.name)

        # Load industry knowledge
        if _INDUSTRY_ROOT.exists():
            for f in _INDUSTRY_ROOT.glob("*"):
                if f.suffix in (".md", ".json", ".txt"):
                    self.add_industry_doc(f.name)

        # Load framework knowledge
        if _FRAMEWORK_ROOT.exists():
            for f in _FRAMEWORK_ROOT.glob("*"):
                if f.suffix in (".md", ".json", ".txt"):
                    self.add_framework_doc(f.name)


# Singleton instance
_vector_store: Optional[VectorStore] = None


def get_vector_store(persist_dir: str = DEFAULT_PERSIST_DIR) -> VectorStore:
    """Get the singleton vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(persist_dir=persist_dir)
    return _vector_store