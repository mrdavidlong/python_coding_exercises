# Insertion Sort
#
# Concept: Build the sorted portion of the array one element at a time.
# For each new element, shift all larger elements in the sorted portion one
# position to the right to make room, then insert the new element into its
# correct position. Analogous to sorting a hand of playing cards.
#
# Time complexity:
#   Best:    O(n)    — already sorted; each element needs zero shifts
#   Average: O(n²)
#   Worst:   O(n²)  — reverse-sorted input; every element shifts all the way
#
# Space complexity: O(1) — in-place
#
# Stable: YES — the while-loop condition uses strict '>' so equal elements are
#   never shifted past each other.
#
# When to use:
#   - Small arrays (n ≲ 20): low constant factors beat O(n log n) algorithms.
#   - Nearly sorted data: close to O(n) in practice.
#   - Online/streaming input: can sort as elements arrive without seeing the
#     whole array upfront.
#   - Often used as the base case inside Timsort and Introsort.

from typing import List


def insertion_sort(nums: List[int]) -> List[int]:
    for i in range(1, len(nums)):
        # Hold the element to be inserted into the sorted portion.
        key = nums[i]
        j = i - 1
        # Shift elements that are greater than 'key' one position to the
        # right to open a slot for 'key'.
        while j >= 0 and nums[j] > key:
            nums[j + 1] = nums[j]
            j -= 1
        # Insert 'key' into its correct sorted position.
        nums[j + 1] = key
    return nums
