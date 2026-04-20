import pytest
from heap_array import MinHeapArray
from heap_tree import MinHeapTree
from heapify_and_heapsort import heapify, heapsort, heapify_simple, heapsort_simple

HEAP_IMPLEMENTATIONS = [MinHeapArray, MinHeapTree]

@pytest.fixture(params=HEAP_IMPLEMENTATIONS)
def Heap(request):
    return request.param


# ---------------------------------------------------------------------------
# Shared tests — run against both MinHeapArray and MinHeapTree
# ---------------------------------------------------------------------------

def test_push_and_pop_min_order(Heap):
    # Push 3, 1, 2; min-heap must always pop the smallest element first
    h = Heap()
    h.push(3)
    h.push(1)
    h.push(2)
    assert h.pop() == 1
    assert h.pop() == 2
    assert h.pop() == 3


def test_peek_does_not_remove(Heap):
    # peek returns the minimum but leaves it in the heap; pop still returns it
    h = Heap()
    h.push(5)
    h.push(2)
    h.push(8)
    assert h.peek() == 2
    assert h.pop() == 2


def test_pop_empty_returns_none(Heap):
    # Popping an empty heap returns None rather than raising an error
    h = Heap()
    assert h.pop() is None


def test_peek_empty_returns_none(Heap):
    # Peeking an empty heap returns None rather than raising an error
    h = Heap()
    assert h.peek() is None


def test_is_empty(Heap):
    # is_empty is True on a new heap, False after a push, True after all pops
    h = Heap()
    assert h.is_empty()
    h.push(1)
    assert not h.is_empty()
    h.pop()
    assert h.is_empty()


def test_size(Heap):
    # size tracks the element count correctly across pushes and pops
    h = Heap()
    assert h.size() == 0
    h.push(10)
    h.push(20)
    assert h.size() == 2
    h.pop()
    assert h.size() == 1


def test_single_element(Heap):
    # A heap with one element should peek and pop that element, then be empty
    h = Heap()
    h.push(42)
    assert h.peek() == 42
    assert h.pop() == 42
    assert h.is_empty()


def test_duplicate_values(Heap):
    # Equal values must all be returned; order among equals is unspecified but
    # every value must appear exactly once
    h = Heap()
    for v in [3, 3, 1, 1, 2]:
        h.push(v)
    result = []
    while not h.is_empty():
        result.append(h.pop())
    assert result == sorted([3, 3, 1, 1, 2])


def test_push_already_sorted(Heap):
    # Pushing already-sorted values (ascending) still produces correct min ordering
    h = Heap()
    for v in [1, 2, 3, 4, 5]:
        h.push(v)
    assert h.pop() == 1
    assert h.pop() == 2


def test_push_reverse_sorted(Heap):
    # Pushing reverse-sorted values exercises the most sift-ups
    h = Heap()
    for v in [5, 4, 3, 2, 1]:
        h.push(v)
    result = []
    while not h.is_empty():
        result.append(h.pop())
    assert result == [1, 2, 3, 4, 5]


def test_interleaved_push_pop(Heap):
    # Interleaving pushes and pops must maintain the heap property at each step
    h = Heap()
    h.push(5)
    h.push(3)
    assert h.pop() == 3
    h.push(1)
    assert h.pop() == 1
    assert h.pop() == 5


# ---------------------------------------------------------------------------
# heapify tests
# ---------------------------------------------------------------------------

def test_heapify_satisfies_heap_property():
    # After heapify, every parent must be <= its children (min-heap property)
    nums = [9, 4, 7, 1, 3, 6, 2, 8, 5]
    heapify(nums)
    n = len(nums)
    for i in range(n // 2):
        left  = 2 * i + 1
        right = 2 * i + 2
        assert nums[i] <= nums[left], f"heap[{i}]={nums[i]} > left child [{left}]={nums[left]}"
        if right < n:
            assert nums[i] <= nums[right], f"heap[{i}]={nums[i]} > right child [{right}]={nums[right]}"


def test_heapify_minimum_at_root():
    # The smallest element must be at index 0 after heapify
    nums = [5, 3, 8, 1, 9, 2]
    heapify(nums)
    assert nums[0] == 1


def test_heapify_already_valid():
    # A valid heap should remain a valid heap after heapify
    nums = [1, 3, 2, 7, 5, 4]
    heapify(nums)
    assert nums[0] == 1


def test_heapify_single_element():
    nums = [42]
    heapify(nums)
    assert nums == [42]


def test_heapify_empty():
    nums = []
    heapify(nums)
    assert nums == []


def test_heapify_duplicates():
    # Duplicates should be handled without breaking the heap property
    nums = [3, 3, 1, 1, 2, 2]
    heapify(nums)
    assert nums[0] == 1


# ---------------------------------------------------------------------------
# heapify_simple tests
# ---------------------------------------------------------------------------

def test_heapify_simple_satisfies_heap_property():
    # After heapify_simple, every parent must be <= its children
    nums = [9, 4, 7, 1, 3, 6, 2, 8, 5]
    heapify_simple(nums)
    n = len(nums)
    for i in range(n // 2):
        left  = 2 * i + 1
        right = 2 * i + 2
        assert nums[i] <= nums[left]
        if right < n:
            assert nums[i] <= nums[right]


def test_heapify_simple_minimum_at_root():
    nums = [5, 3, 8, 1, 9, 2]
    heapify_simple(nums)
    assert nums[0] == 1


def test_heapify_simple_duplicates():
    nums = [3, 3, 1, 1, 2, 2]
    heapify_simple(nums)
    assert nums[0] == 1


def test_heapify_simple_single_element():
    nums = [42]
    heapify_simple(nums)
    assert nums == [42]


def test_heapify_simple_empty():
    nums = []
    heapify_simple(nums)
    assert nums == []


# ---------------------------------------------------------------------------
# heapsort tests  (efficient — in-place, O(1) space)
# ---------------------------------------------------------------------------

def test_heapsort_basic():
    # [3,1,2] reversed; sorted result is [1,2,3]
    assert heapsort([3, 1, 2]) == [1, 2, 3]


def test_heapsort_already_sorted():
    assert heapsort([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_heapsort_reverse_sorted():
    assert heapsort([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


def test_heapsort_duplicates():
    assert heapsort([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]


def test_heapsort_single_element():
    assert heapsort([7]) == [7]


def test_heapsort_empty():
    assert heapsort([]) == []


def test_heapsort_negative_numbers():
    assert heapsort([0, -1, 4, -3, 2]) == [-3, -1, 0, 2, 4]


def test_heapsort_large():
    import random
    nums = list(range(200, 0, -1))
    random.shuffle(nums)
    assert heapsort(nums) == list(range(1, 201))


# ---------------------------------------------------------------------------
# heapsort_simple tests  (simple — min-heap + output list, O(n) space)
# ---------------------------------------------------------------------------

def test_heapsort_simple_basic():
    assert heapsort_simple([3, 1, 2]) == [1, 2, 3]


def test_heapsort_simple_already_sorted():
    assert heapsort_simple([1, 2, 3, 4, 5]) == [1, 2, 3, 4, 5]


def test_heapsort_simple_reverse_sorted():
    assert heapsort_simple([5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5]


def test_heapsort_simple_duplicates():
    assert heapsort_simple([3, 1, 2, 1, 3]) == [1, 1, 2, 3, 3]


def test_heapsort_simple_single_element():
    assert heapsort_simple([7]) == [7]


def test_heapsort_simple_empty():
    assert heapsort_simple([]) == []


def test_heapsort_simple_negative_numbers():
    assert heapsort_simple([0, -1, 4, -3, 2]) == [-3, -1, 0, 2, 4]


# ---------------------------------------------------------------------------
# Test runners
# ---------------------------------------------------------------------------

SHARED_HEAP_TESTS = [
    test_push_and_pop_min_order,
    test_peek_does_not_remove,
    test_pop_empty_returns_none,
    test_peek_empty_returns_none,
    test_is_empty,
    test_size,
    test_single_element,
    test_duplicate_values,
    test_push_already_sorted,
    test_push_reverse_sorted,
    test_interleaved_push_pop,
]

if __name__ == "__main__":
    for Heap in HEAP_IMPLEMENTATIONS:
        for test in SHARED_HEAP_TESTS:
            test(Heap)

    test_heapify_satisfies_heap_property()
    test_heapify_minimum_at_root()
    test_heapify_already_valid()
    test_heapify_single_element()
    test_heapify_empty()
    test_heapify_duplicates()

    test_heapify_simple_satisfies_heap_property()
    test_heapify_simple_minimum_at_root()
    test_heapify_simple_duplicates()
    test_heapify_simple_single_element()
    test_heapify_simple_empty()

    test_heapsort_basic()
    test_heapsort_already_sorted()
    test_heapsort_reverse_sorted()
    test_heapsort_duplicates()
    test_heapsort_single_element()
    test_heapsort_empty()
    test_heapsort_negative_numbers()
    test_heapsort_large()

    test_heapsort_simple_basic()
    test_heapsort_simple_already_sorted()
    test_heapsort_simple_reverse_sorted()
    test_heapsort_simple_duplicates()
    test_heapsort_simple_single_element()
    test_heapsort_simple_empty()
    test_heapsort_simple_negative_numbers()

    print("All tests passed.")
