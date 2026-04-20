from typing import List


# ===========================================================================
# heapify — convert an arbitrary list into a min-heap
# ===========================================================================
#
# Two versions are provided:
#
#   heapify        — Floyd's bottom-up algorithm  — O(n) time,  O(1) space
#   heapify_simple — sift-up each element         — O(n log n), O(1) space
#
# Both produce a valid min-heap in-place; the difference is only efficiency.


# ---------------------------------------------------------------------------
# heapify — Floyd's bottom-up O(n) algorithm  (main / efficient version)
# ---------------------------------------------------------------------------
#
# Key insight: every LEAF node is trivially a valid 1-element heap already.
# In a 0-indexed array heap the leaves occupy indices n//2 through n-1,
# so there is no need to touch them. We only process the INTERNAL nodes
# (those that have at least one child), starting from the LAST internal node
# at index n//2 - 1 and working upward to the root.
#
# Why is this O(n) rather than O(n log n)?
#   Nodes at the BOTTOM of the tree are numerous but have SHORT sift paths.
#   Nodes near the TOP have long sift paths but there are very FEW of them.
#   Summing across all levels:
#     level 0 (root)       :  1 node,  ≤ log n swaps
#     level 1              :  2 nodes, ≤ log n - 1 swaps each
#     ...
#     level log n - 1      :  n/2 nodes, ≤ 1 swap each
#   The geometric series Σ k·(n/2^k) converges to 2n, so total work = O(n).
#
# Time:  O(n)   — tighter than it looks; see analysis above
# Space: O(1)   — all swaps happen inside the original array

def heapify(nums: List[int]) -> None:
    """Convert nums into a min-heap in-place using Floyd's O(n) algorithm."""
    n = len(nums)
    # Start at the last internal node and sift each one down to its correct
    # position. Leaves (index >= n//2) are skipped — they need no work.
    for i in range(n // 2 - 1, -1, -1):
        _sift_down_min(nums, n, i)


def _sift_down_min(nums: List[int], heap_size: int, i: int) -> None:
    # Repeatedly swap node i with its SMALLER child until the min-heap
    # property holds: every node <= both its children.
    #
    # Child index formulas (0-indexed):
    #   left  child of i  →  2*i + 1
    #   right child of i  →  2*i + 2
    #
    # We look for the smallest among {i, left, right} and swap i with it.
    # If i is already the smallest, the heap property holds — stop.
    while True:
        smallest = i
        left  = 2 * i + 1
        right = 2 * i + 2
        if left  < heap_size and nums[left]  < nums[smallest]:
            smallest = left
        if right < heap_size and nums[right] < nums[smallest]:
            smallest = right
        if smallest == i:
            # Neither child is smaller; heap property is satisfied here.
            break
        nums[i], nums[smallest] = nums[smallest], nums[i]
        i = smallest   # Follow the swapped element down and repeat.


# ---------------------------------------------------------------------------
# heapify_simple — sift-up each element  (simple / educational version)
# ---------------------------------------------------------------------------
#
# Treat the list as if it were being built from scratch: grow the "valid
# heap" region from the left one element at a time. For each new element
# at index i, bubble it UP through its ancestors until the heap property
# holds. This mirrors how push() works on a heap class.
#
# Time:  O(n log n) — each of n elements may sift up O(log n) levels.
#   In the worst case (reverse-sorted input) every element travels all
#   the way to the root.
#
# Space: O(1)       — in-place, just like the efficient version.
#
# Compared to heapify:
#   heapify_simple does MORE work because it sifts UP, and sifting up
#   starts at the BOTTOM of the tree where there are the MOST nodes and
#   the LONGEST paths. Floyd's algorithm sifts DOWN, where the longest
#   paths are at the top but there are very FEW nodes there.

def heapify_simple(nums: List[int]) -> None:
    """Convert nums into a min-heap in-place by sifting up each element."""
    for i in range(1, len(nums)):
        # nums[0..i-1] is already a valid min-heap.
        # Insert nums[i] into it by bubbling it up to its correct position.
        _sift_up(nums, i)


def _sift_up(nums: List[int], i: int) -> None:
    # Walk upward from index i toward the root (index 0).
    # Parent of node i is always at (i - 1) // 2.
    #
    # Visual layout of a 7-element heap (0-indexed):
    #
    #          0
    #         / \
    #        1   2
    #       / \ / \
    #      3  4 5  6
    #
    #   parent(1)=0, parent(2)=0
    #   parent(3)=1, parent(4)=1, parent(5)=2, parent(6)=2
    #
    while i > 0:
        parent = (i - 1) // 2
        if nums[i] < nums[parent]:
            # Current node is smaller than its parent — swap upward.
            nums[i], nums[parent] = nums[parent], nums[i]
            i = parent
        else:
            # Heap property satisfied; no more swaps needed on this path.
            break


# ===========================================================================
# heapsort — sort a list in ascending order
# ===========================================================================
#
# Two versions are provided:
#
#   heapsort        — in-place max-heap sort  — O(n log n), O(1) space
#   heapsort_simple — min-heap + output list  — O(n log n), O(n) space
#
# Both produce the same sorted result; the difference is memory usage.


# ---------------------------------------------------------------------------
# heapsort — in-place sort with a max-heap  (main / efficient version)
# ---------------------------------------------------------------------------
#
# Why a MAX-heap and not a min-heap?
#   We want to sort IN PLACE with O(1) extra space. If we used a min-heap
#   we would pop the minimum to a separate output list (O(n) space).
#   With a max-heap, each extraction swaps the root (current maximum) to
#   the END of the array — exactly where it belongs in ascending order —
#   so no extra list is ever needed.
#
# Two phases:
#   Phase 1 — build a max-heap in O(n) using Floyd's bottom-up trick.
#             After this step nums[0] holds the largest element.
#
#   Phase 2 — extract n-1 times:
#     • Swap nums[0] (current max) with nums[end] (last unsorted element).
#       nums[end] is now in its final sorted position — we never touch it again.
#     • Shrink the logical heap boundary by 1 (end decreases by 1).
#     • Sift the new root DOWN to restore the max-heap property over [0, end).
#
# Time:  O(n log n) — O(n) build + n × O(log n) sift-downs
# Space: O(1)       — all operations are in-place; only loop variables on stack
# Stable: NO        — long-range swaps during sift-down can reorder equal elements

def heapsort(nums: List[int]) -> List[int]:
    """Sort nums in ascending order in-place and return it."""
    n = len(nums)

    # Phase 1: Build a max-heap in O(n).
    # Same Floyd bottom-up approach as heapify, but using _sift_down_max
    # so the LARGEST element bubbles to the root.
    for i in range(n // 2 - 1, -1, -1):
        _sift_down_max(nums, n, i)

    # Phase 2: Repeatedly move the current maximum to its final position.
    for end in range(n - 1, 0, -1):
        # nums[0] is the largest element in the unsorted region [0..end].
        # Swap it to position 'end', which is its correct sorted position.
        nums[0], nums[end] = nums[end], nums[0]
        # The element now at the root (index 0) is likely out of place.
        # Sift it down over the REDUCED heap [0..end-1] to restore order.
        _sift_down_max(nums, end, 0)

    return nums


def _sift_down_max(nums: List[int], heap_size: int, i: int) -> None:
    # Push element at index i down until it is >= both its children
    # (max-heap property: every node >= its children).
    while True:
        largest = i
        left  = 2 * i + 1
        right = 2 * i + 2
        if left  < heap_size and nums[left]  > nums[largest]:
            largest = left
        if right < heap_size and nums[right] > nums[largest]:
            largest = right
        if largest == i:
            break
        nums[i], nums[largest] = nums[largest], nums[i]
        i = largest


# ---------------------------------------------------------------------------
# heapsort_simple — min-heap + output list  (simple / educational version)
# ---------------------------------------------------------------------------
#
# The straightforward reading of "use a heap to sort":
#   1. Heapify the input into a min-heap so nums[0] is always the minimum.
#   2. Repeatedly pop the minimum into a result list until the heap is empty.
#
# Each pop() is O(log n) and we do it n times → O(n log n) total, same
# asymptotic time as the efficient version.
#
# The cost is O(n) EXTRA SPACE for the result list. The efficient version
# avoids this by sorting in-place with a max-heap.
#
# Time:  O(n log n) — heapify O(n) + n pops each O(log n)
# Space: O(n)       — result list holds all n elements outside the input array

def heapsort_simple(nums: List[int]) -> List[int]:
    """Sort nums in ascending order and return a new sorted list."""
    if not nums:
        return nums

    # Step 1: Rearrange nums into a min-heap so the smallest is at index 0.
    heapify(nums)

    result = []
    heap_size = len(nums)

    while heap_size > 0:
        # The root (index 0) is always the current minimum in a min-heap.
        result.append(nums[0])

        # To remove the root without shifting every other element (O(n)),
        # overwrite it with the LAST element in the heap and shrink the
        # heap boundary by 1. The tree shape stays complete; only the
        # heap ORDER property may be violated at the root.
        heap_size -= 1
        if heap_size > 0:
            nums[0] = nums[heap_size]
            # The element now at the root is likely larger than its children.
            # Sift it down to restore the min-heap property.
            _sift_down_min(nums, heap_size, 0)

    return result
