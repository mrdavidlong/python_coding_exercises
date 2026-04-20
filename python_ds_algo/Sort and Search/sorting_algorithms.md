# Sorting Algorithms Reference

| File | Algorithm | Time (Best / Average / Worst) | Space | Stable |
|---|---|---|---|---|
| `bubble_sort.py` | Bubble Sort | O(n) / O(n²) / O(n²) | O(1) | Yes |
| `insertion_sort.py` | Insertion Sort | O(n) / O(n²) / O(n²) | O(1) | Yes |
| `selection_sort.py` | Selection Sort | O(n²) / O(n²) / O(n²) | O(1) | No |
| `merge_sort.py` | Merge Sort | O(n log n) / O(n log n) / O(n log n) | O(n) | Yes |
| `array_quick_sort.py` | Quick Sort | O(n log n) / O(n log n) / O(n²) | O(log n) | No |
| `array_quick_sort_optimized.py` | Quick Sort (Randomized) | O(n log n) / O(n log n) / O(n²) | O(log n) | No |
| `heap_sort.py` | Heap Sort | O(n log n) / O(n log n) / O(n log n) | O(1) | No |
| `array_counting_sort.py` | Counting Sort | O(n + k) / O(n + k) / O(n + k) | O(k) | Yes |
| `radix_sort.py` | Radix Sort (LSD) | O(d·(n+k)) / O(d·(n+k)) / O(d·(n+k)) | O(n + k) | Yes |
| `bucket_sort.py` | Bucket Sort | O(n + k) / O(n + k) / O(n²) | O(n + k) | Yes |
| `linked_list_sort.py` | Merge Sort (Linked List) | O(n log n) / O(n log n) / O(n log n) | O(log n) | Yes |

---
## Summary:
- Bubble / Selection — avoid in production; bubble if nearly-sorted, selection only if minimizing writes matters                                   
- Insertion — small arrays or nearly-sorted data; the base case inside Timsort/Introsort
- Merge — need guaranteed O(n log n) + stability; best for linked lists and external (disk) sorting                                                
- Quick — best average-case speed in practice; use randomized pivot to avoid O(n²); the backbone of std::sort                                      
- Heap — need O(n log n) worst-case and O(1) space; also the fallback in Introsort                                                                 
- Counting — small integer range k = O(n); e.g. scores, ages, enum values                                                                          
- Radix — large integer range but fixed-width keys; outperforms comparison sorts on millions of integers                                           
- Bucket — uniformly distributed floats or integers; parallelizable  

---

## Bubble Sort

**Time:**
- **Best O(n):** When the array is already sorted the early-exit flag detects a full pass with no swaps and stops after a single pass through all n elements.
- **Average/Worst O(n²):** Each of the n passes scans up to n elements. In the worst case (reverse-sorted input) every adjacent pair is out of order, producing n²/2 comparisons and swaps.

**Space O(1):** Only a constant number of variables (loop indices, `swapped` flag) are used; all swaps are done in-place.

**Stable:** Equal elements are never swapped (the condition is strict `>`), so their original relative order is preserved.

**When to use:**
- Rarely used in production; mainly for teaching the concept of sorting.
- Acceptable for very small arrays (n ≲ 10) where simplicity matters more than speed.
- Useful when input is nearly sorted and the O(n) best case is likely to trigger often.
- Avoid for any non-trivial dataset — O(n²) average makes it impractical at scale.

---

## Insertion Sort

**Time:**
- **Best O(n):** On already-sorted input the inner while-loop condition fails immediately for every element — each is compared once and inserted in place without any shifting.
- **Average/Worst O(n²):** For each of the n elements, up to i shifts are needed to find its position in the sorted prefix. This sums to 1 + 2 + … + (n-1) = n(n-1)/2 in the worst case (reverse-sorted input).

**Space O(1):** Sorting is done in-place by shifting elements within the same array; only the `key` variable and index pointers are needed.

**Stable:** The while-loop uses strict `>` so equal elements are never shifted past each other, preserving their original order.

**When to use:**
- Small arrays (n ≲ 20): low constant factors often beat O(n log n) algorithms at this scale.
- Nearly sorted data: each element needs very few shifts, keeping it close to O(n) in practice.
- Online / streaming input: can insert each new element into the sorted prefix as it arrives, without needing the full array upfront.
- Used as the base case inside Timsort (Python's built-in) and Introsort (C++ `std::sort`) for small subarrays.
- Avoid for large or randomly ordered data — O(n²) average dominates.

---

## Selection Sort

**Time O(n²) in all cases:** The algorithm always scans the entire remaining unsorted portion to find the minimum, regardless of input order. There is no early exit — even if the array is already sorted, all n(n-1)/2 comparisons are still made. Only the number of swaps benefits (at most n-1 swaps total).

**Space O(1):** In-place; only index variables are needed.

**Not stable:** The minimum element is swapped directly into position i, which can jump it over equal elements that appeared earlier in the array.

**When to use:**
- When minimizing the number of writes matters more than minimizing comparisons — selection sort does at most n-1 swaps regardless of input, whereas insertion sort or bubble sort may swap O(n²) times. Useful when writing to storage is expensive (e.g. flash memory with limited write cycles).
- Otherwise, prefer insertion sort for small arrays — it has the same O(1) space and O(n²) time but is faster in practice due to fewer comparisons on average and a useful O(n) best case.

---

## Merge Sort

**Time O(n log n) in all cases:** The array is split in half at each level, producing log n levels of recursion. At every level, the merge step touches all n elements. Because the split is always at the midpoint, the depth never varies with input order — best, average, and worst are all identical.

**Space O(n):** Each merge creates a new output list combining the two halves. Although sub-lists are freed after each merge, at peak usage O(n) auxiliary memory is live. The call stack adds O(log n), which is dominated by the O(n) merge buffers.

**Stable:** The merge step resolves ties by picking the left element first (`<=`), so equal elements from the left half always appear before those from the right half, preserving original order.

**When to use:**
- When a guaranteed O(n log n) worst case is required and O(n) extra memory is acceptable.
- When stability is required and the dataset is too large for insertion sort.
- Sorting linked lists: merge sort requires only sequential access and can be implemented with O(1) extra space on linked lists (unlike arrays where O(n) buffers are needed).
- External sorting (data too large for RAM): the sequential merge access pattern is efficient for disk I/O; classic k-way merge sort is the standard approach.
- Avoid when memory is constrained — heap sort gives the same O(n log n) guarantee with O(1) space.

---

## Quick Sort

**Time:**
- **Best/Average O(n log n):** When pivots split the array into roughly equal halves, the recursion depth is log n and each level does O(n) partition work.
- **Worst O(n²):** Occurs when the pivot is always the minimum or maximum (e.g. already-sorted input with a last-element pivot). This produces maximally unbalanced partitions of size 0 and n-1, giving n levels each doing O(n) work.

**Space O(log n) average / O(n) worst:** No extra array is allocated, but each recursive call uses a stack frame. Balanced splits give O(log n) call depth; degenerate splits give O(n).

**Not stable:** The partition step performs long-range swaps that can reorder equal elements.

**When to use:**
- General-purpose in-memory sorting when average-case performance is the priority — quicksort is typically 2-3x faster than merge sort or heap sort in practice due to better cache locality (partitioning touches sequential memory).
- When the O(n²) worst case is mitigated: use randomized pivot selection or the median-of-three heuristic to make worst case extremely unlikely.
- When stability is not required and O(log n) stack space is acceptable.
- Avoid on nearly-sorted or reverse-sorted input with a naive pivot strategy — use randomized pivot or switch to Timsort instead.
- The foundation of Introsort (used in C++ `std::sort`): starts as quicksort and falls back to heap sort if recursion depth exceeds 2·log n, getting the best of both.

---

## Heap Sort

**Time O(n log n) in all cases:** Building the max-heap takes O(n) (heapify from the bottom up). Each of the n-1 extract steps swaps the root to the end and restores the heap in O(log n) with sift-down. The total is O(n) + O(n log n) = O(n log n), with no variation for input order.

**Space O(1):** The heap is built directly inside the input array. Sift-down is iterative in this implementation, so only O(1) stack space is used.

**Not stable:** Sift-down performs long-range swaps across the heap structure, which can move equal elements past each other.

**When to use:**
- When both O(n log n) worst-case time and O(1) space are required simultaneously — the only common algorithm that achieves both.
- Memory-constrained environments (embedded systems, OS kernels) where merge sort's O(n) buffer is unaffordable and quicksort's O(n²) worst case is too risky.
- Also useful as a building block: a min-heap variant efficiently implements a priority queue for problems like k-way merge, top-k elements, or Dijkstra's algorithm.
- Avoid when stability is needed or when cache performance matters — heap sort's non-sequential memory access makes it slower than quicksort by a significant constant factor in practice.

---

## Counting Sort

**Time O(n + k) in all cases** where `k = max(nums) + 1` (the size of the count array):
- One pass over n elements to populate the count array.
- One pass over k buckets to build the output.
- Time is dominated by whichever is larger. When k >> n the algorithm is slower than comparison sorts; it is only practical when k = O(n).

**Space O(k):** The count array has k entries. The result list adds O(n), but k is typically the dominant term. Requires **non-negative integers**; negatives need offset normalization.

**Stable:** Elements with the same value are appended in the order they appear in the count (index order), preserving relative order.

**When to use:**
- Sorting integers when the value range k is small relative to n (k = O(n)) — e.g. sorting exam scores (0–100) for thousands of students, or ages, grades, or small enums.
- When both O(n) time and stable ordering are needed and the integer-only constraint is acceptable.
- Avoid when k >> n (e.g. sorting a handful of values that could be anywhere in 0–10⁹) — the O(k) space and time make it worse than comparison sorts. Use radix sort instead for large-range integers.

---

## Radix Sort (LSD)

**Time O(d · (n + k))** where `d` = number of digits in the largest value, `k` = base (10):
- Each of the d digit passes runs a stable counting sort in O(n + k).
- For fixed-width integers (e.g. 32-bit), d is constant, simplifying to O(n).
- For arbitrarily large values, d = O(log₁₀(max)) so worst case is O(n log max).

**Space O(n + k):** Each digit pass needs an output buffer of size n and a count array of size k (10 for base-10). Requires **non-negative integers**.

**Stable:** Each per-digit counting sort is stable (right-to-left traversal preserves earlier pass ordering), which is essential — without stability, results from previous digit passes would be destroyed.

**When to use:**
- Sorting large arrays of non-negative integers when the value range is too large for counting sort but d (number of digits) is small — e.g. sorting millions of 32-bit integers: d = 10 decimal digits, so O(10n) ≈ O(n).
- When a linear-time stable sort is needed on fixed-width keys (phone numbers, ZIP codes, IP addresses, fixed-length strings).
- Avoid for floating-point numbers or variable-length strings without special encoding. For negative integers, add an offset to shift all values non-negative first.

---

## Bucket Sort

**Time:**
- **Best/Average O(n + k):** With k buckets and uniformly distributed input, each bucket holds ~n/k elements. Sorting each small bucket takes O((n/k) log(n/k)) and summed over k buckets this approaches O(n) when k ≈ n.
- **Worst O(n²):** When all elements land in a single bucket (highly skewed distribution), sorting that bucket degrades to the complexity of the per-bucket sort (Python's Timsort is O(m log m), but with m = n the total becomes O(n log n); a naive O(m²) per-bucket sort would give O(n²)).

**Space O(n + k):** n elements are distributed across k bucket lists. The total number of stored elements is always n, plus k empty list objects.

**Stable:** Python's built-in `sorted()` is stable (Timsort), and elements are appended to buckets in their original order, so relative order among equal elements is preserved.

**When to use:**
- Floating-point numbers uniformly distributed in a known range (the classic use case) — each bucket holds ~1 element on average, giving near-O(n) performance.
- Integers with a known bounded range that are roughly uniformly distributed, where distributing into buckets reduces the per-bucket work to near O(1).
- Parallel sorting: buckets are fully independent and can be sorted concurrently across multiple threads or machines.
- Avoid for skewed or clustered data where most values fall in the same range — degenerate bucket sizes eliminate the speedup. Use radix sort or counting sort instead when distribution is unknown or uneven.
