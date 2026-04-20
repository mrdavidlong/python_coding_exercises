# Min-Heap — Explicit Tree-Based Implementation
#
# Concept: The same logical complete binary tree as the array heap, but
# each node is a separate object with left/right/parent pointers.
#
# The key challenge with an explicit tree is finding the "next" insertion
# position (the leftmost open slot on the bottom level) and the "last"
# node (needed when popping the root) — operations that are trivial with
# array indexing.
#
# Bit-navigation trick (Floyd/Knuth): for a heap of size n, the node at
# 1-indexed position p can be reached from the root by reading the binary
# representation of p, skipping the leading 1-bit, and following the
# remaining bits: 0 → go left, 1 → go right.
#
#   p=1  (  1) →  ""   → root itself
#   p=2  ( 10) →  "0"  → left  child of root
#   p=3  ( 11) →  "1"  → right child of root
#   p=4  (100) →  "00" → root → left → left
#   p=5  (101) →  "01" → root → left → right
#
# New node is inserted at position (size + 1); the last node to remove on
# pop is at position size. Parent of position p is at p // 2.
#
# Operations and complexity:
#   push(x)   O(log n) — navigate to insertion point, link node, sift up
#   pop()     O(log n) — copy last-node value to root, unlink last, sift down
#   peek()    O(1)     — read root value
#   _find     O(log n) — bit-navigation through tree

from typing import Optional


class _Node:
    __slots__ = ("val", "left", "right", "parent")

    def __init__(self, val: int) -> None:
        self.val    = val
        self.left:   Optional["_Node"] = None
        self.right:  Optional["_Node"] = None
        self.parent: Optional["_Node"] = None


class MinHeapTree:
    def __init__(self) -> None:
        self._root: Optional[_Node] = None
        self._size: int = 0

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def push(self, val: int) -> None:
        self._size += 1
        node = _Node(val)
        if self._size == 1:
            self._root = node
            return
        # The parent of the new node is at position size // 2.
        parent = self._find(self._size // 2)
        node.parent = parent
        # Even position → left child; odd position → right child.
        if self._size % 2 == 0:
            parent.left = node
        else:
            parent.right = node
        self._sift_up(node)

    def pop(self) -> Optional[int]:
        if self._root is None:
            return None
        min_val = self._root.val
        if self._size == 1:
            self._root = None
            self._size = 0
            return min_val
        # Copy the last node's value into the root, then unlink the last node.
        # This avoids having to re-wire the tree structure after a removal.
        last = self._find(self._size)
        self._root.val = last.val
        # Detach the last node from its parent.
        if last is last.parent.right:
            last.parent.right = None
        else:
            last.parent.left = None
        self._size -= 1
        self._sift_down(self._root)
        return min_val

    def peek(self) -> Optional[int]:
        return self._root.val if self._root else None

    def is_empty(self) -> bool:
        return self._size == 0

    def size(self) -> int:
        return self._size

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _find(self, pos: int) -> _Node:
        # Navigate from root to the node at 1-indexed position pos using
        # the binary representation of pos (skip the leading '1' bit).
        # bin(pos) returns e.g. '0b101'; [3:] strips '0b1' leaving '01'.
        path = bin(pos)[3:]
        node = self._root
        for bit in path:
            node = node.left if bit == "0" else node.right
        return node

    def _sift_up(self, node: _Node) -> None:
        # Swap values upward while the current node is smaller than its parent.
        while node.parent and node.val < node.parent.val:
            node.val, node.parent.val = node.parent.val, node.val
            node = node.parent

    def _sift_down(self, node: _Node) -> None:
        # Swap values downward with the smaller child until heap order holds.
        while node:
            smallest = node
            if node.left  and node.left.val  < smallest.val:
                smallest = node.left
            if node.right and node.right.val < smallest.val:
                smallest = node.right
            if smallest is node:
                break
            node.val, smallest.val = smallest.val, node.val
            node = smallest
