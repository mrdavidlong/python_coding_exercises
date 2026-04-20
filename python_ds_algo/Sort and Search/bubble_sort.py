# Bubble Sort
#
# Concept: Repeatedly step through the array comparing adjacent pairs and
# swapping them if they're out of order. Each full pass "bubbles" the largest
# unsorted element to its correct position at the end. An early-exit flag
# makes it adaptive: if a full pass produces no swaps the array is already
# sorted and we stop immediately.
#
# Time complexity:
#   Best:    O(n)    — already sorted; inner loop runs once with no swaps
#   Average: O(n²)
#   Worst:   O(n²)  — reverse-sorted input
#
# Space complexity: O(1) — in-place, only a constant number of pointers
#
# Stable: YES — equal elements are never swapped, so their relative order is
#   preserved.
#
# When to use:
#   - Educational purposes; rarely used in production.
#   - Useful when the input is nearly sorted and the O(n) best case matters.
#   - Avoid for large or randomly ordered data — O(n²) average is too slow.

from typing import List


def bubble_sort(nums: List[int]) -> List[int]:
    n = len(nums)
    for i in range(n):
        swapped = False
        # After each pass, the last i elements are already in their final
        # positions, so we only need to compare up to n - 1 - i.
        for j in range(n - 1 - i):
            if nums[j] > nums[j + 1]:
                nums[j], nums[j + 1] = nums[j + 1], nums[j]
                swapped = True
        # If no swaps occurred the array is already sorted; stop early.
        if not swapped:
            break
    return nums
