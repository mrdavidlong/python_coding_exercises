# Heap Sort
#
# Concept: Two-phase algorithm that uses a max-heap built directly in the
# input array.
#   Phase 1 (heapify): Build a max-heap from the array in O(n) time by
#     sifting down from the last internal node to the root.
#   Phase 2 (extract): Repeatedly swap the root (maximum) with the last
#     unsorted element, shrink the heap boundary by one, and restore the
#     heap property with a sift-down. After n-1 extractions the array is
#     sorted in ascending order.
#
# Time complexity:
#   Best:    O(n log n)
#   Average: O(n log n)
#   Worst:   O(n log n) — guaranteed; no bad pivot choice like quicksort
#
# Space complexity: O(1) — in-place; the heap is stored inside the input array
#
# Stable: NO — the long-range swaps during sift-down can change the relative
#   order of equal elements.
#
# When to use:
#   - When O(n log n) worst-case AND O(1) extra space are both required.
#   - Embedded/memory-constrained environments where merge sort's O(n) space
#     is unacceptable but quicksort's O(n²) worst case is risky.
#   - Less cache-friendly than quicksort in practice due to non-sequential
#     memory access patterns; typically slower by a constant factor.

from typing import List


def heap_sort(nums: List[int]) -> List[int]:
    n = len(nums)
    # Phase 1: Build a max-heap in-place.
    # Start from the last internal node (n // 2 - 1) and sift down to root.
    for i in range(n // 2 - 1, -1, -1):
        _sift_down(nums, n, i)
    # Phase 2: Extract the maximum element one at a time.
    for i in range(n - 1, 0, -1):
        # The root holds the current maximum; move it to its sorted position.
        nums[0], nums[i] = nums[i], nums[0]
        # Restore the heap property for the reduced heap of size i.
        _sift_down(nums, i, 0)
    return nums


def _sift_down(nums: List[int], heap_size: int, root: int) -> None:
    # Push the element at 'root' down until the max-heap property holds.
    while True:
        largest = root
        left = 2 * root + 1
        right = 2 * root + 2
        if left < heap_size and nums[left] > nums[largest]:
            largest = left
        if right < heap_size and nums[right] > nums[largest]:
            largest = right
        if largest == root:
            break
        nums[root], nums[largest] = nums[largest], nums[root]
        root = largest
