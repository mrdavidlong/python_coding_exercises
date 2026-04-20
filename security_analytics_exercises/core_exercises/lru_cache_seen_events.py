"""
Problem: The XDR pipeline needs to track recently-seen event fingerprints to
avoid reprocessing the same event if it arrives twice (e.g., from duplicate
feeds). Implement an LRU (Least Recently Used) cache with a fixed capacity.

How LRU eviction works with OrderedDict:
---------------------------------------------------------------------------

  OrderedDict maintains insertion order. We use the convention:
    LEFT end  = Least Recently Used  (eviction candidate)
    RIGHT end = Most Recently Used

  capacity = 3

  add("A")  →  [A]
  add("B")  →  [A, B]
  add("C")  →  [A, B, C]        ← full
  add("A")  →  [B, C, A]        ← A re-accessed → moved to RIGHT (MRU end)
  add("D")  →  [C, A, D]        ← B was LEFT (LRU) → evicted; D inserted at RIGHT
  add("E")  →  [A, D, E]        ← C evicted

  Key operations:
    move_to_end(key)         → promotes key to MRU (right end)
    popitem(last=False)      → removes and returns LRU item (left end)

  Why not a regular dict?
    Python 3.7+ dicts preserve insertion order, but they lack move_to_end()
    and the O(1) popitem(last=False). OrderedDict gives us both.

  contains() intentionally does NOT call move_to_end — a read-only check
  should not change the eviction order.

API:
    cache = SeenEventsCache(capacity=3)
    cache.add("fingerprint-abc")      → True if new, False if already seen
    cache.contains("fingerprint-abc") → True/False
    cache.size()                      → int
"""

from collections import OrderedDict


class SeenEventsCache:
    """Fixed-capacity LRU cache for event fingerprints.

    Values are always None — we only care about key presence/order.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        # OrderedDict: left = LRU, right = MRU
        # e.g. OrderedDict([("fp-abc", None), ("fp-def", None), ("fp-xyz", None)])
        #                    ^oldest/LRU                          ^newest/MRU
        self._store: OrderedDict[str, None] = OrderedDict()

    def add(self, fingerprint: str) -> bool:
        """Record a fingerprint as seen, evicting the LRU entry if the cache is full.

        If already present, refreshes it to MRU so it won't be evicted soon.

        Args:
            fingerprint: Unique string identifying an event (e.g. a hash).
                         e.g. "sha256:abc123"

        Returns:
            True  — fingerprint was new (first time seen).
            False — fingerprint was already in the cache (duplicate).
        """
        if fingerprint in self._store:
            # Refresh: move to the MRU end so it's evicted last
            self._store.move_to_end(fingerprint)
            return False   # already seen

        if len(self._store) >= self.capacity:
            # Pop the item at the LEFT (least recently used)
            self._store.popitem(last=False)

        # Insert new fingerprint at the RIGHT (most recently used)
        self._store[fingerprint] = None
        return True   # newly seen

    def contains(self, fingerprint: str) -> bool:
        """Check if a fingerprint is cached WITHOUT updating LRU order.

        A read-only check — does not promote the entry to MRU. This ensures
        a monitoring health-check won't accidentally keep stale entries alive.

        Args:
            fingerprint: e.g. "sha256:abc123"

        Returns:
            True if present in cache, False otherwise.
        """
        return fingerprint in self._store

    def size(self) -> int:
        return len(self._store)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_new_fingerprint_returns_true():
    cache = SeenEventsCache(capacity=3)
    assert cache.add("fp-001") is True


def test_duplicate_fingerprint_returns_false():
    cache = SeenEventsCache(capacity=3)
    cache.add("fp-001")
    assert cache.add("fp-001") is False


def test_evicts_lru_when_at_capacity():
    cache = SeenEventsCache(capacity=2)
    cache.add("fp-001")           # store: [fp-001]
    cache.add("fp-002")           # store: [fp-001, fp-002]
    cache.add("fp-001")           # refresh fp-001 → store: [fp-002, fp-001]
    cache.add("fp-003")           # fp-002 is LRU → evicted; store: [fp-001, fp-003]
    assert cache.contains("fp-001") is True
    assert cache.contains("fp-003") is True
    assert cache.contains("fp-002") is False  # was LRU when fp-003 arrived


def test_size_respects_capacity():
    cache = SeenEventsCache(capacity=3)
    cache.add("a")
    cache.add("b")
    cache.add("c")
    cache.add("d")  # evicts 'a'; size stays at 3
    assert cache.size() == 3


def test_contains_does_not_affect_lru_order():
    # After adding fp-001 then fp-002, fp-001 is LRU.
    # Calling contains() on fp-001 must NOT refresh it.
    cache = SeenEventsCache(capacity=2)
    cache.add("fp-001")
    cache.add("fp-002")
    cache.contains("fp-001")     # read-only — does NOT promote fp-001
    cache.add("fp-003")          # fp-001 (still LRU) should be evicted
    assert cache.contains("fp-001") is False


def test_invalid_capacity_raises():
    try:
        SeenEventsCache(capacity=0)
        assert False
    except ValueError:
        pass


def test_capacity_one():
    cache = SeenEventsCache(capacity=1)
    cache.add("a")
    cache.add("b")   # evicts "a"
    assert cache.contains("b") is True
    assert cache.contains("a") is False


if __name__ == "__main__":
    test_new_fingerprint_returns_true()
    test_duplicate_fingerprint_returns_false()
    test_evicts_lru_when_at_capacity()
    test_size_respects_capacity()
    test_contains_does_not_affect_lru_order()
    test_invalid_capacity_raises()
    test_capacity_one()
    print("All tests passed.")
