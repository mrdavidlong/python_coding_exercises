from typing import List


def selection_sort(nums: List[int]) -> List[int]:
    n = len(nums)
    for i in range(n):
        # Find the index of the minimum element in the unsorted portion.
        min_index = i
        for j in range(i + 1, n):
            if nums[j] < nums[min_index]:
                min_index = j
        # Swap the found minimum with the first element of the unsorted
        # portion.
        nums[i], nums[min_index] = nums[min_index], nums[i]
    return nums
