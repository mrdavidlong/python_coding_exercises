from dataclasses import FrozenInstanceError
import heapq

import pytest

from Python_Fundamentals.data_models import PriorityItem, Vertex


def test_frozen_equality_repr_hash_and_ordering() -> None:
    first = PriorityItem(1, 0, {"payload": 1})
    same_rank = PriorityItem(1, 0, "different payload")
    assert first == same_rank
    assert hash(first) == hash(same_rank)
    assert "PriorityItem" in repr(first)
    with pytest.raises(FrozenInstanceError):
        first.priority = 2  # type: ignore[misc]


def test_heap_tie_breaking_uses_sequence_not_payload() -> None:
    heap = [PriorityItem(1, 2, object()), PriorityItem(1, 1, object())]
    heapq.heapify(heap)
    assert heapq.heappop(heap).sequence == 1


def test_class_instance_static_and_dunder_methods() -> None:
    before = Vertex.created
    vertex = Vertex.from_value(12)
    renamed = vertex.renamed("node")
    assert (vertex.label, renamed.label) == ("12", "node")
    assert Vertex.created == before + 2
    assert Vertex.valid_label(" x ") and not Vertex.valid_label("")
    assert len(renamed) == 4
