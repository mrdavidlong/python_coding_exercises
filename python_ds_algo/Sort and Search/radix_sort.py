# Radix Sort (LSD — Least Significant Digit)
#
# Concept: Non-comparison sort that processes integers digit by digit, from
# the least significant to the most significant. At each digit position a
# stable counting sort (base 10) groups elements into buckets 0-9 without
# disturbing the relative order established by previous passes. After d passes
# (where d is the number of digits in the largest value) the array is sorted.
#
# Time complexity:
#   Best:    O(d * (n + k))  where d = digits in max value, k = base (10)
#   Average: O(d * (n + k))
#   Worst:   O(d * (n + k))
#   When d is constant (fixed-width integers), this simplifies to O(n).
#
# Space complexity: O(n + k) — output buffer of size n plus count array of
#   size k (10 for base-10).
#
# Stable: YES — each counting-sort pass is stable, which is essential for
#   correctness across multiple digit passes.
#
# Constraints:
#   - Only works on NON-NEGATIVE integers in this implementation.
#   - Negative numbers require offset normalization or a sign-handling step.
#   - Not suitable for floating-point numbers without special encoding.
#
# When to use:
#   - Sorting large arrays of integers with a bounded number of digits.
#   - Faster than comparison sorts when d << log n (e.g. sorting 32-bit ints).
#   - Common in database systems and network packet routing tables.

from typing import List


def radix_sort(nums: List[int]) -> List[int]:
    if not nums:
        return nums
    max_val = max(nums)
    # Process one digit place at a time, starting from the units digit.
    exp = 1
    while max_val // exp > 0:
        _counting_sort_by_digit(nums, exp)
        exp *= 10
    return nums


def _counting_sort_by_digit(nums: List[int], exp: int) -> None:
    # Stable counting sort on the digit at position 'exp' (1, 10, 100, ...).
    n = len(nums)
    output = [0] * n
    count = [0] * 10  # Digits 0-9

    # Count occurrences of each digit at the current position.
    for num in nums:
        digit = (num // exp) % 10
        count[digit] += 1

    # Convert counts to cumulative counts (prefix sums) so count[d] holds
    # the last valid output index for digit d.
    for i in range(1, 10):
        count[i] += count[i - 1]

    # Traverse right-to-left to keep the sort stable.
    for i in range(n - 1, -1, -1):
        digit = (nums[i] // exp) % 10
        output[count[digit] - 1] = nums[i]
        count[digit] -= 1

    # Copy the sorted pass back into the original array.
    for i in range(n):
        nums[i] = output[i]
