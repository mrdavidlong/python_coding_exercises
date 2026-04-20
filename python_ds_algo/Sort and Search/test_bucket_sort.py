from bucket_sort import bucket_sort

def test_basic():
    # [3,2,1] reversed order; sorted result is [1,2,3]
    assert bucket_sort([3, 2, 1]) == [1, 2, 3]

def test_single_element():
    # Single element needs no sorting; returns [1]
    assert bucket_sort([1]) == [1]

def test_empty():
    # Empty list should return empty list
    assert bucket_sort([]) == []

def test_two_elements():
    # Two elements; sorted result is [1,2]
    assert bucket_sort([2, 1]) == [1, 2]

def test_already_sorted():
    # Already sorted [1,2,3] should remain [1,2,3]
    assert bucket_sort([1, 2, 3]) == [1, 2, 3]

def test_reverse_sorted():
    # [5,4,3,2,1] is fully reversed; sorted result is [1,2,3,4,5]
    assert bucket_sort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]

def test_with_duplicates():
    # [3,1,2,1,3] has duplicate values; sorted result is [1,1,2,3,3]
    # Bucket sort is stable since Python's sort is stable
    assert bucket_sort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]

def test_all_duplicates():
    # All identical elements; order unchanged, returns [2,2,2]
    # This is the case where min_val == max_val, returns early
    assert bucket_sort([2, 2, 2]) == [2, 2, 2]

def test_negative_numbers():
    # Negative numbers; bucket sort normalizes by min_val
    # [0,-1,4,-3,2] normalized and distributed across buckets
    assert bucket_sort([0, -1, 4, -3, 2]) == [-3, -1, 0, 2, 4]

def test_wide_range():
    # Values spread across a wide range
    # [100,1,50,25,75] distributed into buckets
    assert bucket_sort([100, 1, 50, 25, 75]) == [1, 25, 50, 75, 100]

def test_uniform_distribution():
    # Uniformly distributed values; best case O(n + k)
    # [10,20,30,40,50,60,70,80,90] evenly spaced
    assert bucket_sort([90, 10, 50, 30, 70, 20, 80, 40, 60]) == [10, 20, 30, 40, 50, 60, 70, 80, 90]

def test_skewed_distribution():
    # Skewed distribution with many values in same range
    # [1,2,3,4,5,100,101,102] most values clustered at low end
    assert bucket_sort([100, 1, 102, 3, 101, 2, 4, 5]) == [1, 2, 3, 4, 5, 100, 101, 102]

if __name__ == "__main__":
    test_basic()
    test_single_element()
    test_empty()
    test_two_elements()
    test_already_sorted()
    test_reverse_sorted()
    test_with_duplicates()
    test_all_duplicates()
    test_negative_numbers()
    test_wide_range()
    test_uniform_distribution()
    test_skewed_distribution()
    print("All tests passed.")
