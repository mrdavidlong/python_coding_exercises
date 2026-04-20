from quick_sort_optimized import sort_array

def test_basic():
    # [3,2,1] reversed order; sorted result is [1,2,3]
    assert sort_array([3, 2, 1]) == [1, 2, 3]

def test_single_element():
    # Single element needs no sorting; returns [1]
    assert sort_array([1]) == [1]

def test_empty():
    # Empty list should return empty list
    assert sort_array([]) == []

def test_already_sorted():
    # Already sorted [1,2,3] should remain [1,2,3]
    # Randomized pivot reduces chance of O(n²) worst case
    assert sort_array([1, 2, 3]) == [1, 2, 3]

def test_reverse_sorted():
    # [5,4,3,2,1] is fully reversed; sorted result is [1,2,3,4,5]
    # With randomized pivot, unlikely to hit O(n²) worst case
    assert sort_array([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_with_duplicates():
    # [3,1,2,1,3] has duplicate values; sorted result is [1,1,2,3,3]
    assert sort_array([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

def test_all_duplicates():
    # All identical elements; order unchanged, returns [2,2,2]
    # Partition puts all equal elements in their sorted position
    assert sort_array([2, 2, 2]) == [2, 2, 2]

def test_negative_numbers():
    # Negative numbers; sorted result is [-3,-1,0,2,4]
    assert sort_array([0, -1, 4, -3, 2]) == [-3, -1, 0, 2, 4]

def test_two_elements_unsorted():
    # Two elements out of order; sorted result is [1,2]
    assert sort_array([2, 1]) == [1, 2]

def test_large_array():
    # Larger array to test quicksort recursion
    # [9,8,7,6,5,4,3,2,1] completely reversed
    assert sort_array([9, 8, 7, 6, 5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_nearly_sorted():
    # Nearly sorted data; randomized pivot prevents degenerate partitions
    # [1,2,3,4,6,5] has one element out of place
    assert sort_array([1, 2, 3, 4, 6, 5]) == [1, 2, 3, 4, 5, 6]

def test_many_duplicates():
    # Array with many duplicate values
    # [1,3,1,2,3,2,1,3,2] has repetitions
    assert sort_array([1, 3, 1, 2, 3, 2, 1, 3, 2]) == [1, 1, 1, 2, 2, 2, 3, 3, 3]

if __name__ == "__main__":
    test_basic()
    test_single_element()
    test_empty()
    test_already_sorted()
    test_reverse_sorted()
    test_with_duplicates()
    test_all_duplicates()
    test_negative_numbers()
    test_two_elements_unsorted()
    test_large_array()
    test_nearly_sorted()
    test_many_duplicates()
    print("All tests passed.")
