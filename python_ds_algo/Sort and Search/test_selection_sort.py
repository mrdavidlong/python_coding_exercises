from selection_sort import selection_sort

def test_basic():
    # [3,2,1] reversed order; sorted result is [1,2,3]
    assert selection_sort([3, 2, 1]) == [1, 2, 3]

def test_single_element():
    # Single element needs no sorting; returns [1]
    assert selection_sort([1]) == [1]

def test_empty():
    # Empty list should return empty list
    assert selection_sort([]) == []

def test_already_sorted():
    # Already sorted [1,2,3] should remain [1,2,3]
    assert selection_sort([1, 2, 3]) == [1, 2, 3]

def test_reverse_sorted():
    # [5,4,3,2,1] is fully reversed; sorted result is [1,2,3,4,5]
    assert selection_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_with_duplicates():
    # [3,1,2,1,3] has duplicate values; sorted result is [1,1,2,3,3]
    assert selection_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

def test_all_duplicates():
    # All identical elements; order unchanged, returns [2,2,2]
    assert selection_sort([2, 2, 2]) == [2, 2, 2]

def test_negative_numbers():
    # Negative numbers; sorted result is [-3,-1,0,2,4]
    assert selection_sort([0, -1, 4, -3, 2]) == [-3, -1, 0, 2, 4]

if __name__ == "__main__":
    test_basic()
    test_single_element()
    test_empty()
    test_already_sorted()
    test_reverse_sorted()
    test_with_duplicates()
    test_all_duplicates()
    test_negative_numbers()
    print("All tests passed.")
