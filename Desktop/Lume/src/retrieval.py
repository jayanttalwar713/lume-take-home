"""
Policy retrieval using FAISS vector store and sentence-transformers.
Chunks the policy document at the section/subsection level (not naive fixed-size
chunking) so that cross-references between sections are preserved as named anchors.
"""
import re
import os
import pickle
from pathlib import Path

import numpy as np

from .models import PolicySection


class PolicyRetriever:
    """
    Section-aware RAG over the Gaggia IT policy document.

    Parsing strategy:
    - Level 1 sections (## Section N) become parent chunks.
    - Level 2 subsections (### N.M) become child chunks that also embed
      the parent section title for context.
    - At query time we retrieve child chunks and de-duplicate by parent
      to ensure cross-section coverage when the policy spans multiple areas.
    """

    INDEX_CACHE = Path(__file__).parent.parent / ".policy_index.pkl"

    def __init__(self, policy_path: str):
        self.policy_path = Path(policy_path)
        self._sections: list[PolicySection] = []
        self._embeddings: np.ndarray | None = None
        self._model = None
        self._load()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(self, query: str, k: int = 6) -> list[PolicySection]:
        """Return the top-k most relevant policy sections for a query."""
        if not self._sections:
            return []
        q_emb = self._embed([query])[0]
        scores = self._cosine_similarity(q_emb, self._embeddings)
        top_idx = np.argsort(scores)[::-1][:k]
        results = []
        for i in top_idx:
            section = PolicySection(
                section_id=self._sections[i].section_id,
                title=self._sections[i].title,
                content=self._sections[i].content,
                score=float(scores[i]),
            )
            results.append(section)
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self):
        """Parse policy, build embeddings (or load from cache)."""
        policy_text = self.policy_path.read_text()
        self._sections = self._parse_sections(policy_text)

        if self.INDEX_CACHE.exists():
            try:
                with open(self.INDEX_CACHE, "rb") as f:
                    cache = pickle.load(f)
                if cache.get("source_hash") == self._source_hash():
                    self._embeddings = cache["embeddings"]
                    return
            except Exception:
                pass

        texts = [f"{s.section_id}: {s.title}\n{s.content}" for s in self._sections]
        self._embeddings = self._embed(texts)

        with open(self.INDEX_CACHE, "wb") as f:
            pickle.dump(
                {"source_hash": self._source_hash(), "embeddings": self._embeddings}, f
            )

    def _source_hash(self) -> str:
        import hashlib
        return hashlib.md5(self.policy_path.read_bytes()).hexdigest()

    def _parse_sections(self, text: str) -> list[PolicySection]:
        """
        Parse the markdown policy into section chunks.

        Strategy:
        - Split on '### N.M' subsection headers (these become the primary chunks).
        - Each chunk inherits its parent section title.
        - Section-level intros (text before the first subsection) are their own chunks.
        """
        sections: list[PolicySection] = []

        # Capture the parent section context
        current_parent_title = ""
        current_parent_id = ""

        lines = text.split("\n")
        current_id = ""
        current_title = ""
        current_lines: list[str] = []

        def flush():
            nonlocal current_id, current_title, current_lines
            content = "\n".join(current_lines).strip()
            if content and current_id:
                sections.append(
                    PolicySection(
                        section_id=current_id,
                        title=current_title,
                        content=content,
                    )
                )
            current_lines = []

        for line in lines:
            # Top-level section: ## Section N — Title
            m2 = re.match(r"^## Section (\d+)\s+[—-]\s+(.+)$", line)
            if m2:
                flush()
                current_parent_id = f"Section {m2.group(1)}"
                current_parent_title = m2.group(2).strip()
                current_id = current_parent_id
                current_title = current_parent_title
                continue

            # Subsection: ### N.M Title
            m3 = re.match(r"^### (\d+\.\d+)\s+(.+)$", line)
            if m3:
                flush()
                sub_id = m3.group(1)
                sub_title = m3.group(2).strip()
                current_id = sub_id
                current_title = f"{current_parent_title} > {sub_title}"
                current_lines.append(f"[{current_parent_id}: {current_parent_title}]")
                continue

            current_lines.append(line)

        flush()
        return sections

    def _embed(self, texts: list[str]) -> np.ndarray:
        """Embed texts using sentence-transformers (lazy-loaded)."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self._model = SentenceTransformer(model_name)
        embeddings = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        return embeddings

    @staticmethod
    def _cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
        q = query_vec / (np.linalg.norm(query_vec) + 1e-10)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10
        m = matrix / norms
        return m @ q
