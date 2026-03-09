"""
Periodic re-clustering: merge similar clusters (PROJECT_SPEC_CONTINUATION §4.5).
"""
import logging
from typing import List

logger = logging.getLogger("ai.clustering.recluster")


class ReClusterJob:
    """Merge clusters that have become too similar (DBSCAN on centroids)."""

    MERGE_DISTANCE_THRESHOLD = 0.25

    def merge_similar_clusters(self, clusterer) -> None:
        """Find and merge clusters that are too similar."""
        clusters = getattr(clusterer, "clusters", [])
        if len(clusters) < 2:
            return
        try:
            import numpy as np
        except ImportError:
            return
        centroids = []
        for c in clusters:
            cent = getattr(c, "centroid", None)
            if cent is not None and hasattr(cent, "__len__") and len(cent) > 0:
                centroids.append(np.asarray(cent))
            else:
                centroids.append(np.zeros(384))
        if not centroids:
            return
        X = np.array(centroids)
        sim = np.dot(X, X.T)
        dist = 1 - sim
        from sklearn.cluster import DBSCAN
        db = DBSCAN(eps=self.MERGE_DISTANCE_THRESHOLD, min_samples=1, metric="precomputed")
        labels = db.fit_predict(dist)
        groups = {}
        for idx, label in enumerate(labels):
            groups.setdefault(int(label), []).append(idx)
        for label, indices in groups.items():
            if len(indices) <= 1:
                continue
            to_merge = [clusters[i] for i in indices]
            self._merge_group(clusterer, to_merge)

    def _merge_group(self, clusterer, to_merge: List):
        primary = to_merge[0]
        for secondary in to_merge[1:]:
            primary.posts.extend(getattr(secondary, "posts", []))
            for attr in ("companies", "products", "features"):
                a = set(getattr(primary, attr, []))
                a.update(getattr(secondary, attr, []))
                setattr(primary, attr, list(a))
            primary.source_count = len(primary.posts)
            try:
                import numpy as np
                c1 = getattr(primary, "centroid", None)
                c2 = getattr(secondary, "centroid", None)
                if c1 is not None and c2 is not None:
                    primary.centroid = (np.asarray(c1) + np.asarray(c2)) / 2.0
                    norm = np.linalg.norm(primary.centroid)
                    if norm > 0:
                        primary.centroid = primary.centroid / norm
            except Exception:
                pass
            if getattr(secondary, "first_seen", ""):
                if not getattr(primary, "first_seen", "") or secondary.first_seen < primary.first_seen:
                    primary.first_seen = secondary.first_seen
            if getattr(secondary, "last_updated", ""):
                if secondary.last_updated > getattr(primary, "last_updated", ""):
                    primary.last_updated = secondary.last_updated
            try:
                clusterer.clusters.remove(secondary)
            except ValueError:
                pass
