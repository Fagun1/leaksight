"""
Rumor clustering via sentence embeddings and cosine similarity
(PROJECT_SPEC_CONTINUATION §4).
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timezone
import logging

logger = logging.getLogger("ai.clustering")


@dataclass
class RumorCluster:
    cluster_id: str
    centroid: any  # numpy array
    posts: List[str] = field(default_factory=list)
    representative_text: str = ""
    companies: List[str] = field(default_factory=list)
    products: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    first_seen: str = ""
    last_updated: str = ""
    source_count: int = 0
    confidence: float = 0.0


class RumorClusterer:
    """
    Clusters leak posts into rumor groups using sentence embeddings
    and cosine similarity with entity-aware matching.
    """

    SIMILARITY_THRESHOLD_HIGH = 0.80
    SIMILARITY_THRESHOLD_LOW = 0.60
    ENTITY_OVERLAP_THRESHOLD = 0.5

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = None
        self._model_name = model_name
        self.clusters: List[RumorCluster] = []
        self._try_load_model()

    def _try_load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            self.np = np
            self.model = SentenceTransformer(self._model_name)
            logger.info(f"RumorClusterer loaded {self._model_name}")
        except Exception as e:
            logger.warning(f"RumorClusterer: sentence-transformers not available: {e}")

    @property
    def model_name(self):
        return self._model_name

    def embed_text(self, text: str):
        """Generate sentence embedding."""
        if not self.model or not text:
            return None
        import numpy as np
        arr = self.model.encode(text[:2000], normalize_embeddings=True)
        return np.asarray(arr)

    def cosine_similarity(self, vec_a, vec_b) -> float:
        if vec_a is None or vec_b is None:
            return 0.0
        import numpy as np
        return float(np.dot(vec_a, vec_b))

    def entity_overlap(self, entities_a: dict, entities_b: dict) -> float:
        """Jaccard similarity of entity sets."""
        set_a = set()
        set_b = set()
        for key in ("companies", "products", "features"):
            set_a.update((e or "").lower() for e in entities_a.get(key, []))
            set_b.update((e or "").lower() for e in entities_b.get(key, []))
        if not set_a and not set_b:
            return 0.0
        inter = len(set_a & set_b)
        union = len(set_a | set_b)
        return inter / union if union else 0.0

    def assign_to_cluster(
        self,
        post_id: str,
        text: str,
        entities: dict,
    ) -> Tuple[Optional[str], bool]:
        """
        Assign a post to an existing cluster or create a new one.
        Returns (cluster_id, is_new_cluster).
        """
        import numpy as np
        embedding = self.embed_text(text or "")
        if embedding is None:
            new_id = f"rumor_{post_id}"
            self.clusters.append(RumorCluster(
                cluster_id=new_id,
                centroid=np.zeros(384) if hasattr(np, 'zeros') else [],
                posts=[post_id],
                representative_text=(text or "")[:200],
                companies=entities.get("companies", []),
                products=entities.get("products", []),
                features=entities.get("features", []),
                first_seen=datetime.now(timezone.utc).isoformat(),
                last_updated=datetime.now(timezone.utc).isoformat(),
                source_count=1,
                confidence=0.3,
            ))
            return (new_id, True)

        best_cluster = None
        best_similarity = 0.0
        for cluster in self.clusters:
            if not hasattr(cluster.centroid, "__len__") or len(cluster.centroid) == 0:
                continue
            sim = self.cosine_similarity(embedding, cluster.centroid)
            if sim > best_similarity:
                best_similarity = sim
                best_cluster = cluster

        now = datetime.now(timezone.utc).isoformat()

        if best_similarity >= self.SIMILARITY_THRESHOLD_HIGH and best_cluster:
            self._add_to_cluster(best_cluster, post_id, embedding, entities, now)
            return (best_cluster.cluster_id, False)

        if (
            self.SIMILARITY_THRESHOLD_LOW <= best_similarity < self.SIMILARITY_THRESHOLD_HIGH
            and best_cluster
        ):
            cluster_entities = {
                "companies": best_cluster.companies,
                "products": best_cluster.products,
                "features": best_cluster.features,
            }
            if self.entity_overlap(entities, cluster_entities) >= self.ENTITY_OVERLAP_THRESHOLD:
                self._add_to_cluster(best_cluster, post_id, embedding, entities, now)
                return (best_cluster.cluster_id, False)

        new_id = f"rumor_{post_id}"
        new_cluster = RumorCluster(
            cluster_id=new_id,
            centroid=embedding,
            posts=[post_id],
            representative_text=(text or "")[:200],
            companies=entities.get("companies", []),
            products=entities.get("products", []),
            features=entities.get("features", []),
            first_seen=now,
            last_updated=now,
            source_count=1,
            confidence=0.3,
        )
        self.clusters.append(new_cluster)
        return (new_id, True)

    def _add_to_cluster(self, cluster: RumorCluster, post_id: str, embedding, entities: dict, timestamp: str):
        import numpy as np
        cluster.posts.append(post_id)
        cluster.source_count = len(cluster.posts)
        cluster.last_updated = timestamp
        n = len(cluster.posts)
        cluster.centroid = (cluster.centroid * (n - 1) + embedding) / n
        norm = np.linalg.norm(cluster.centroid)
        if norm > 0:
            cluster.centroid = cluster.centroid / norm
        for key in ("companies", "products", "features"):
            existing = set(getattr(cluster, key, []))
            existing.update(entities.get(key, []))
            setattr(cluster, key, list(existing))
        cluster.confidence = min(0.95, 0.3 + 0.1 * cluster.source_count)
