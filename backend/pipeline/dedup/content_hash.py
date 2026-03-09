"""
SimHash for near-duplicate text detection (PROJECT_SPEC_CONTINUATION §1.6).
"""
import hashlib
from typing import List


def simhash(text: str, hash_bits: int = 64) -> int:
    """Compute SimHash fingerprint for near-duplicate text detection."""
    if not text:
        return 0
    tokens = text.lower().split()
    vector = [0] * hash_bits

    for token in tokens:
        token_hash = int(
            hashlib.md5(token.encode("utf-8")).hexdigest(), 16
        ) & ((1 << hash_bits) - 1)
        for i in range(hash_bits):
            if token_hash & (1 << i):
                vector[i] += 1
            else:
                vector[i] -= 1

    fingerprint = 0
    for i in range(hash_bits):
        if vector[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint


def hamming_distance(hash1: int, hash2: int) -> int:
    """Count differing bits between two hashes."""
    return bin(hash1 ^ hash2).count("1")


def is_near_duplicate(hash1: int, hash2: int, threshold: int = 3) -> bool:
    """Two documents are near-duplicates if hamming distance <= threshold."""
    return hamming_distance(hash1, hash2) <= threshold
