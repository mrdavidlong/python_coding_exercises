# Merge Sort
#
# Concept: Divide-and-conquer. Recursively split the array in half until each
# subarray has one element (trivially sorted), then repeatedly merge pairs of
# sorted subarrays into a single sorted array. The key insight is that merging
# two sorted arrays takes O(n) time with two pointers.
#
# Time complexity:
#   Best:    O(n log n) — log n split levels, O(n) merge work per level
#   Average: O(n log n)
#   Worst:   O(n log n) — guaranteed regardless of input order
#
# Space complexity: O(n) — auxiliary arrays are created during each merge step
#
# Stable: YES — the merge step picks the left element first on a tie, so equal
#   elements preserve their original relative order.
#
# When to use:
#   - When a guaranteed O(n log n) worst case is required (unlike quicksort).
#   - When stability matters and the data doesn't fit in cache (e.g. external
#     sort on disk), because its access pattern is sequential.
#   - Sorting linked lists: no random access needed, and O(1) extra space is
#     achievable with in-place merging.
#   - Trade-off: extra O(n) memory makes it less cache-friendly than heapsort
#     for in-memory sorting.

from typing import List


def merge_sort(nums: List[int]) -> List[int]:
    # Base case: a list of 0 or 1 element is already sorted.
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left = merge_sort(nums[:mid])
    right = merge_sort(nums[mid:])
    return _merge(left, right)


def _merge(left: List[int], right: List[int]) -> List[int]:
    result = []
    i = j = 0
    # Compare the front of each half and append the smaller element.
    while i < len(left) and j < len(right):
        # '<=' preserves stability: left element wins on a tie.
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # Append any remaining elements from either half.
    result.extend(left[i:])
    result.extend(right[j:])
    return result
