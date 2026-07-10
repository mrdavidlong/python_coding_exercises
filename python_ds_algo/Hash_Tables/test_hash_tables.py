from dataclasses import dataclass

import pytest

from Hash_Tables import ChainedHashTable, LinearProbingHashTable

TABLES = [ChainedHashTable, LinearProbingHashTable]


@dataclass(frozen=True)
class CollisionKey:
    value: str

    def __hash__(self) -> int:
        return 1


@pytest.mark.parametrize("table_type", TABLES)
def test_mapping_contract_and_collisions(table_type) -> None:
    table = table_type(capacity=4)
    keys = [CollisionKey(str(i)) for i in range(3)]
    for index, key in enumerate(keys):
        table[key] = index
    assert len(table) == 3
    assert [table[key] for key in keys] == [0, 1, 2]
    assert dict(table.items()) == dict(zip(keys, range(3)))


@pytest.mark.parametrize("table_type", TABLES)
def test_delete_preserves_colliding_lookup(table_type) -> None:
    table = table_type(capacity=4)
    first, middle, last = map(CollisionKey, "abc")
    table.update({first: 1, middle: 2, last: 3})
    del table[middle]
    assert table[first] == 1
    assert table[last] == 3
    with pytest.raises(KeyError):
        table[middle]


@pytest.mark.parametrize("table_type", TABLES)
def test_update_does_not_grow_or_change_size(table_type) -> None:
    table = table_type(capacity=2, max_load_factor=0.5)
    table["key"] = 1
    capacity = table.capacity
    table["key"] = 2
    assert table["key"] == 2
    assert len(table) == 1
    assert table.capacity == capacity


@pytest.mark.parametrize("table_type", TABLES)
def test_resize_rehashes_entries(table_type) -> None:
    table = table_type(capacity=2, max_load_factor=0.5)
    for value in range(20):
        table[value] = value * value
    assert table.capacity > 2
    assert [table[value] for value in range(20)] == [value * value for value in range(20)]


@pytest.mark.parametrize("table_type", TABLES)
def test_missing_and_invalid_configuration(table_type) -> None:
    table = table_type()
    with pytest.raises(KeyError):
        table["missing"]
    with pytest.raises(KeyError):
        del table["missing"]
    with pytest.raises(ValueError):
        table_type(capacity=1)
    with pytest.raises(TypeError):
        table_type(capacity=2.5)
    with pytest.raises(ValueError):
        table_type(max_load_factor=0)
