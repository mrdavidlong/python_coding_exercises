import pytest
from counting_sort import sort_array_counting_sort

IMPLEMENTATIONS = [sort_array_counting_sort]

@pytest.fixture(params=IMPLEMENTATIONS)
def fn(request):
    return request.param

def test_basic(fn):
    # [3,2,1] sorted ascending is [1,2,3]
    assert fn([3, 2, 1]) == [1, 2, 3]

def test_empty(fn):
    # Empty list has nothing to sort; result is also empty
    assert fn([]) == []

def test_single_element(fn):
    # Single element is already sorted
    assert fn([1]) == [1]

def test_with_duplicates(fn):
    # [3,3,2,1,2] has duplicate values; counting sort handles them correctly
    assert fn([3, 3, 2, 1, 2]) == [1, 2, 2, 3, 3]

def test_all_same(fn):
    # All elements are equal; result preserves count with all 0s
    assert fn([0, 0, 0]) == [0, 0, 0]

if __name__ == "__main__":
    for fn in IMPLEMENTATIONS:
        test_basic(fn)
        test_empty(fn)
        test_single_element(fn)
        test_with_duplicates(fn)
        test_all_same(fn)
    print("All tests passed.")
