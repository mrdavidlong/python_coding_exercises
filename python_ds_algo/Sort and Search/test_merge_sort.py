from merge_sort import merge_sort

def test_basic():
    # [3,2,1] reversed order; sorted result is [1,2,3]
    assert merge_sort([3, 2, 1]) == [1, 2, 3]

def test_single_element():
    # Single element needs no sorting; returns [1]
    assert merge_sort([1]) == [1]

def test_empty():
    # Empty list should return empty list
    assert merge_sort([]) == []

def test_already_sorted():
    # Already sorted [1,2,3] should remain [1,2,3]
    # Merge sort always guarantees O(n log n) regardless of input order
    assert merge_sort([1, 2, 3]) == [1, 2, 3]

def test_reverse_sorted():
    # [5,4,3,2,1] is fully reversed; sorted result is [1,2,3,4,5]
    # Merge sort handles this efficiently in O(n log n)
    assert merge_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_with_duplicates():
    # [3,1,2,1,3] has duplicate values; sorted result is [1,1,2,3,3]
    # Merge sort is stable; equal elements preserve relative order
    assert merge_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

def test_all_duplicates():
    # All identical elements; order unchanged, returns [2,2,2]
    assert merge_sort([2, 2, 2]) == [2, 2, 2]

def test_negative_numbers():
    # Negative numbers; sorted result is [-3,-1,0,2,4]
    assert merge_sort([0, -1, 4, -3, 2]) == [-3, -1, 0, 2, 4]

def test_two_elements_unsorted():
    # Two elements out of order; sorted result is [1,2]
    assert merge_sort([2, 1]) == [1, 2]

def test_large_array():
    # Larger array to test divide-and-conquer
    # [9,8,7,6,5,4,3,2,1] completely reversed
    assert merge_sort([9, 8, 7, 6, 5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_stability():
    # Test stability: equal elements preserve relative order
    # Using tuples to track original position: [(3,0), (1,1), (2,2), (1,3), (3,4)]
    # After sorting by first element, should maintain order for ties
    # [3,1,2,1,3] -> with tracking would be [(1,1), (1,3), (2,2), (3,0), (3,4)]
    assert merge_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

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
    test_stability()
    print("All tests passed.")
