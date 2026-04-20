import pytest
from quick_sort import sort_array as sort_array_quicksort

IMPLEMENTATIONS = [sort_array_quicksort]

@pytest.fixture(params=IMPLEMENTATIONS)
def fn(request):
    return request.param

def test_basic(fn):
    # [3,2,1] reversed order; sorted result is [1,2,3]
    assert fn([3, 2, 1]) == [1, 2, 3]

def test_single_element(fn):
    # Single element needs no sorting; returns [1]
    assert fn([1]) == [1]

def test_already_sorted(fn):
    # Already sorted [1,2,3] should remain [1,2,3]
    assert fn([1, 2, 3]) == [1, 2, 3]

def test_with_duplicates(fn):
    # [3,1,2,1,3] has duplicate values; sorted result is [1,1,2,3,3]
    assert fn([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

def test_reverse_sorted(fn):
    # [5,4,3,2,1] is fully reversed; sorted result is [1,2,3,4,5]
    assert fn([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

if __name__ == "__main__":
    for fn in IMPLEMENTATIONS:
        test_basic(fn)
        test_single_element(fn)
        test_already_sorted(fn)
        test_with_duplicates(fn)
        test_reverse_sorted(fn)
    print("All tests passed.")
