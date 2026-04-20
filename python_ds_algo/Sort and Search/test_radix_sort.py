from radix_sort import radix_sort

def test_basic():
    # [3,2,1] reversed order; sorted result is [1,2,3]
    assert radix_sort([3, 2, 1]) == [1, 2, 3]

def test_single_element():
    # Single element needs no sorting; returns [1]
    assert radix_sort([1]) == [1]

def test_empty():
    # Empty list should return empty list
    assert radix_sort([]) == []

def test_already_sorted():
    # Already sorted [1,2,3] should remain [1,2,3]
    # Radix sort always guarantees O(d*(n+k)) regardless of input order
    assert radix_sort([1, 2, 3]) == [1, 2, 3]

def test_reverse_sorted():
    # [5,4,3,2,1] is fully reversed; sorted result is [1,2,3,4,5]
    assert radix_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_with_duplicates():
    # [3,1,2,1,3] has duplicate values; sorted result is [1,1,2,3,3]
    # Radix sort is stable since each counting sort pass is stable
    assert radix_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

def test_all_duplicates():
    # All identical elements; order unchanged, returns [2,2,2]
    assert radix_sort([2, 2, 2]) == [2, 2, 2]

def test_two_elements_unsorted():
    # Two elements out of order; sorted result is [1,2]
    assert radix_sort([2, 1]) == [1, 2]

def test_single_digit():
    # Single digit numbers [9,5,3,8,1]
    # Single radix pass needed; sorted result is [1,3,5,8,9]
    assert radix_sort([9, 5, 3, 8, 1]) == [1, 3, 5, 8, 9]

def test_multi_digit():
    # Multi-digit numbers [321,123,231,312,213]
    # Multiple radix passes needed (units, tens, hundreds)
    # Sorted result is [123,213,231,312,321]
    assert radix_sort([321, 123, 231, 312, 213]) == [123, 213, 231, 312, 321]

def test_leading_zeros_equivalent():
    # Numbers with different digit counts [1,10,100,1000]
    # Sorted result maintains order [1,10,100,1000]
    assert radix_sort([1000, 1, 100, 10]) == [1, 10, 100, 1000]

def test_large_numbers():
    # Large numbers test O(d*(n+k)) with larger d
    # [987654,123456,555555,111111] four 6-digit numbers
    assert radix_sort([987654, 123456, 555555, 111111]) == [111111, 123456, 555555, 987654]

def test_zero_included():
    # Including zero; radix sort handles this naturally
    # [5,0,3,0,1] with zeros
    assert radix_sort([5, 0, 3, 0, 1]) == [0, 0, 1, 3, 5]

if __name__ == "__main__":
    test_basic()
    test_single_element()
    test_empty()
    test_already_sorted()
    test_reverse_sorted()
    test_with_duplicates()
    test_all_duplicates()
    test_two_elements_unsorted()
    test_single_digit()
    test_multi_digit()
    test_leading_zeros_equivalent()
    test_large_numbers()
    test_zero_included()
    print("All tests passed.")
