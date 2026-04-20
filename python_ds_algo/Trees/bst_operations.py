# Binary Search Tree Operations
#
# BST Property: for every node N,
#   all values in N's left subtree  < N.val
#   all values in N's right subtree > N.val
#
# This module provides common BST operations as standalone functions,
# all accepting a TreeNode root and returning the (possibly new) root.

from collections import deque
from typing import List, Optional
from tree import TreeNode


# ─────────────────────────────────────────────
#  INSERT
# ─────────────────────────────────────────────

def insert(root: Optional[TreeNode], val: int) -> TreeNode:
    """Insert val into the BST rooted at root.

    Time:  O(h)  h = tree height; O(log n) balanced, O(n) skewed
    Space: O(h)  recursion stack
    Returns the root of the updated tree.
    """
    if root is None:
        return TreeNode(val)
    if val < root.val:
        root.left = insert(root.left, val)
    elif val > root.val:
        root.right = insert(root.right, val)
    # Duplicate values are ignored (BST invariant: unique keys)
    return root


# ─────────────────────────────────────────────
#  FIND / SEARCH
# ─────────────────────────────────────────────

def find(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    """Return the node whose val equals val, or None if not found.

    Time:  O(h)
    Space: O(1)  iterative — no stack overhead
    """
    while root:
        if val == root.val:
            return root
        elif val < root.val:
            root = root.left
        else:
            root = root.right
    return None


# ─────────────────────────────────────────────
#  DELETE
# ─────────────────────────────────────────────

def delete(root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
    """Remove the node with val from the BST and return the new root.

    Three cases:
      1. Node has no children     → simply remove it
      2. Node has one child       → replace node with that child
      3. Node has two children    → replace node's val with its in-order
                                    successor (smallest in right subtree),
                                    then delete the successor from the right
                                    subtree

    Time:  O(h)
    Space: O(h)  recursion stack
    """
    if root is None:
        return None

    if val < root.val:
        root.left = delete(root.left, val)
    elif val > root.val:
        root.right = delete(root.right, val)
    else:
        # Found the node to delete
        if root.left is None:
            return root.right          # Case 1 or 2 (no left child)
        if root.right is None:
            return root.left           # Case 2 (no right child)

        # Case 3: two children — find in-order successor
        successor = _min_node(root.right)
        root.val = successor.val
        root.right = delete(root.right, successor.val)

    return root


def _min_node(node: TreeNode) -> TreeNode:
    """Return the node with the smallest value in the subtree."""
    while node.left:
        node = node.left
    return node


# ─────────────────────────────────────────────
#  TRAVERSALS  (return value lists for easy testing)
# ─────────────────────────────────────────────

def inorder(root: Optional[TreeNode]) -> List[int]:
    """Left → Root → Right.  For a BST this yields values in sorted order.

    Time:  O(n)
    Space: O(h)  recursion stack
    """
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def preorder(root: Optional[TreeNode]) -> List[int]:
    """Root → Left → Right.  Useful for serialising / copying a tree.

    Time:  O(n)
    Space: O(h)
    """
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def postorder(root: Optional[TreeNode]) -> List[int]:
    """Left → Right → Root.  Useful for deletion and expression evaluation.

    Time:  O(n)
    Space: O(h)
    """
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


# ─────────────────────────────────────────────
#  BFS  (level-order)
# ─────────────────────────────────────────────

def bfs(root: Optional[TreeNode]) -> List[List[int]]:
    """Breadth-First Search — returns values level by level.

    Time:  O(n)
    Space: O(w)  w = max width of the tree (up to n/2 for a complete tree)
    """
    if root is None:
        return []
    result: List[List[int]] = []
    queue = deque([root])
    while queue:
        level_size = len(queue)
        level: List[int] = []
        for _ in range(level_size):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


# ─────────────────────────────────────────────
#  LEVEL ORDER FLAT LIST
# ─────────────────────────────────────────────

def level_order_flat(root: Optional[TreeNode]) -> List[int]:
    """Return all node values in level-order (BFS) as a single flat list.

    Unlike bfs() which groups values by level, this returns one flat list
    where values appear left-to-right, top-to-bottom across all levels.

    Example for the BST built from [5, 3, 7, 1, 4, 6, 8]:

         5           Level 0
        / \\
       3   7         Level 1
      / \\ / \\
     1  4 6  8       Level 2

    Returns: [5, 3, 7, 1, 4, 6, 8]

    Time:  O(n)
    Space: O(w)  w = max width of the tree (up to n/2 for a complete tree)
    """
    if root is None:
        return []
    result: List[int] = []
    queue = deque([root])
    while queue:
        node = queue.popleft()
        result.append(node.val)
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
    return result


# ─────────────────────────────────────────────
#  DFS  (iterative pre-order using an explicit stack)
# ─────────────────────────────────────────────

def dfs(root: Optional[TreeNode]) -> List[int]:
    """Depth-First Search — iterative pre-order (Root → Left → Right).

    Using an explicit stack instead of recursion avoids hitting Python's
    default recursion limit on very deep trees.

    Time:  O(n)
    Space: O(h)
    """
    if root is None:
        return []
    result: List[int] = []
    stack = [root]
    while stack:
        node = stack.pop()
        result.append(node.val)
        # Push right first so left is processed first (LIFO)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return result


# ─────────────────────────────────────────────
#  IS VALID BST
# ─────────────────────────────────────────────

def is_valid_bst(root: Optional[TreeNode]) -> bool:
    """Return True if root represents a valid Binary Search Tree.

    Uses min/max bounds threaded down the recursion — simply checking
    left.val < root.val < right.val at each node is not sufficient because
    it misses violations between non-adjacent ancestor/descendant pairs.

    Example of a tree that passes the naive check but is NOT a valid BST:
         5
        / \\
       1   6
          / \\
         4   7       ← 4 < 5, which violates the BST property

    Time:  O(n)
    Space: O(h)
    """
    def _valid(node, lo, hi):
        if node is None:
            return True
        if not (lo < node.val < hi):
            return False
        return _valid(node.left, lo, node.val) and _valid(node.right, node.val, hi)

    return _valid(root, float('-inf'), float('inf'))


# ─────────────────────────────────────────────
#  PRINT TREE  (sideways, right subtree on top)
# ─────────────────────────────────────────────

def print_tree(root: Optional[TreeNode], indent: int = 0, label: str = "Root") -> None:
    """Print the tree rotated 90° counter-clockwise (right subtree on top).

    Example for the BST built from [5, 3, 7, 1, 4, 6, 8]:

        R── 8
      R── 7
        R── 6
    Root── 5
        R── 4
      L── 3
        R── 1   ← wait, 1 has no right, only its position shows indentation

    Reading left-to-right on screen corresponds to bottom-to-top in the tree.
    """
    if root is None:
        if indent == 0:
            print("(empty tree)")
        return
    # Print right subtree first (it appears on top when rotated)
    if root.right:
        print_tree(root.right, indent + 4, "R")
    print(" " * indent + f"{label}── {root.val}")
    if root.left:
        print_tree(root.left, indent + 4, "L")


# ─────────────────────────────────────────────
#  TRAVERSAL PRINT WRAPPERS
# ─────────────────────────────────────────────

def inorder_print(root: Optional[TreeNode]) -> None:
    """Print all values in Left → Root → Right order (sorted for a BST)."""
    print(inorder(root))


def preorder_print(root: Optional[TreeNode]) -> None:
    """Print all values in Root → Left → Right order."""
    print(preorder(root))


def postorder_print(root: Optional[TreeNode]) -> None:
    """Print all values in Left → Right → Root order."""
    print(postorder(root))


def level_by_level_print(root: Optional[TreeNode]) -> None:
    """Print each level of the tree on its own line.

    Example for the BST built from [5, 3, 7, 1, 4, 6, 8]:

        [5]
        [3, 7]
        [1, 4, 6, 8]
    """
    levels = bfs(root)
    if not levels:
        print([])
        return
    for level in levels:
        print(level)
