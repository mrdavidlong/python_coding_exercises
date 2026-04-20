# Bucket Sort
#
# Concept: Distribute elements into a number of buckets spanning the value
# range, sort each bucket individually (using insertion sort or Python's
# built-in sort), then concatenate the buckets in order. Works best when
# input is roughly uniformly distributed so buckets stay small.
#
# Time complexity:
#   Best:    O(n + k)  — uniform distribution; each bucket has ~1 element
#   Average: O(n + k)  — k buckets, n/k elements per bucket on average
#   Worst:   O(n²)     — all elements land in a single bucket; degrades to
#                         the complexity of the per-bucket sort
#
# Space complexity: O(n + k) — n elements distributed across k buckets
#
# Stable: YES — as long as the per-bucket sort is stable (Python's sort is).
#
# Constraints:
#   - Performs poorly on skewed/clustered data (uneven bucket sizes).
#   - For integers with a wide range relative to n, many buckets may be empty;
#     counting sort or radix sort is a better fit in that case.
#   - This implementation supports negative integers by normalizing values
#     relative to the minimum.
#
# When to use:
#   - Floating-point numbers uniformly distributed in [0, 1).
#   - Integers with a known bounded range distributed roughly uniformly.
#   - Parallel sorting: buckets are independent and can be sorted concurrently.

from typing import List


def bucket_sort(nums: List[int]) -> List[int]:
    if len(nums) <= 1:
        return nums

    min_val, max_val = min(nums), max(nums)
    # All elements are equal; nothing to sort.
    if min_val == max_val:
        return nums

    n = len(nums)
    # Each bucket covers an equal share of the value range.
    bucket_size = (max_val - min_val) / n
    buckets: List[List[int]] = [[] for _ in range(n)]

    for num in nums:
        # Map each element to a bucket index in [0, n-1].
        idx = int((num - min_val) / bucket_size)
        # The maximum value maps to index n, clamp it to the last bucket.
        if idx == n:
            idx = n - 1
        buckets[idx].append(num)

    # Sort each bucket and concatenate them in order.
    result: List[int] = []
    for bucket in buckets:
        result.extend(sorted(bucket))  # Python's sort is stable and O(m log m)
    return result
