import io
import contextlib
from tree import TreeNode
from bst_operations import (
    insert, find, delete,
    inorder, preorder, postorder,
    bfs, dfs, level_order_flat,
    is_valid_bst, print_tree,
    inorder_print, preorder_print, postorder_print, level_by_level_print,
)


def capture(fn, *args, **kwargs) -> str:
    """Call fn(*args, **kwargs) and return everything it printed as a string."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue().strip()


# ─────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────

def build_bst(values):
    """Build a BST by inserting values left-to-right."""
    root = None
    for v in values:
        root = insert(root, v)
    return root


def make_tree(val, left=None, right=None):
    """Manually wire up a TreeNode for is_valid_bst edge-case tests."""
    node = TreeNode(val)
    node.left = left
    node.right = right
    return node


# ─────────────────────────────────────────────
#  INSERT
# ─────────────────────────────────────────────

def test_insert_into_empty_tree():
    # Inserting into None creates a root with that value
    root = insert(None, 5)
    assert root.val == 5
    assert root.left is None
    assert root.right is None

def test_insert_smaller_goes_left():
    # 3 < 5 → must be placed as left child
    root = insert(None, 5)
    root = insert(root, 3)
    assert root.left.val == 3

def test_insert_larger_goes_right():
    # 7 > 5 → must be placed as right child
    root = insert(None, 5)
    root = insert(root, 7)
    assert root.right.val == 7

def test_insert_multiple_maintains_bst():
    # Build BST from [5,3,7,1,4,6,8]; inorder must yield sorted sequence
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert inorder(root) == [1, 3, 4, 5, 6, 7, 8]

def test_insert_duplicate_ignored():
    # Inserting an existing value should not change the tree
    root = build_bst([5, 3, 7])
    root = insert(root, 5)
    # Inorder still returns each value once
    assert inorder(root) == [3, 5, 7]


# ─────────────────────────────────────────────
#  FIND
# ─────────────────────────────────────────────

def test_find_existing_value():
    # 4 exists in the tree; returned node must have val == 4
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    node = find(root, 4)
    assert node is not None
    assert node.val == 4

def test_find_root_value():
    # Searching for the root value returns the root itself
    root = build_bst([5, 3, 7])
    assert find(root, 5) is root

def test_find_missing_value():
    # 9 was never inserted; find must return None
    root = build_bst([5, 3, 7])
    assert find(root, 9) is None

def test_find_in_empty_tree():
    # Searching an empty tree always returns None
    assert find(None, 1) is None

def test_find_leaf_node():
    # 1 is a leaf (no children); should still be found correctly
    root = build_bst([5, 3, 7, 1])
    node = find(root, 1)
    assert node is not None
    assert node.val == 1


# ─────────────────────────────────────────────
#  DELETE
# ─────────────────────────────────────────────

def test_delete_leaf_node():
    # Removing a leaf (1) — no children — simply detaches it
    root = build_bst([5, 3, 7, 1, 4])
    root = delete(root, 1)
    assert find(root, 1) is None
    assert inorder(root) == [3, 4, 5, 7]

def test_delete_node_with_one_child():
    # Removing 3 which has only a right child (4)
    # 4 must take 3's place in the tree
    root = build_bst([5, 3, 7, 4])
    root = delete(root, 3)
    assert find(root, 3) is None
    assert inorder(root) == [4, 5, 7]

def test_delete_node_with_two_children():
    # Removing 3 which has both left (1) and right (4) children
    # In-order successor is 4; 4 replaces 3, then old 4 node is removed
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    root = delete(root, 3)
    assert find(root, 3) is None
    assert inorder(root) == [1, 4, 5, 6, 7, 8]

def test_delete_root_node():
    # Removing the root (5); in-order successor is 6
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    root = delete(root, 5)
    assert find(root, 5) is None
    assert inorder(root) == [1, 3, 4, 6, 7, 8]

def test_delete_nonexistent_value():
    # Deleting a value that doesn't exist should leave the tree unchanged
    root = build_bst([5, 3, 7])
    root = delete(root, 99)
    assert inorder(root) == [3, 5, 7]

def test_delete_from_empty_tree():
    # Deleting from None should return None without error
    assert delete(None, 5) is None

def test_delete_only_node():
    # Deleting the single root leaves an empty tree (None)
    root = insert(None, 5)
    root = delete(root, 5)
    assert root is None


# ─────────────────────────────────────────────
#  TRAVERSALS
# ─────────────────────────────────────────────
#
#  BST built from [5, 3, 7, 1, 4, 6, 8]:
#
#          5
#        /   \
#       3     7
#      / \   / \
#     1   4 6   8
#
#  InOrder   → [1, 3, 4, 5, 6, 7, 8]  (sorted)
#  PreOrder  → [5, 3, 1, 4, 7, 6, 8]  (root first)
#  PostOrder → [1, 4, 3, 6, 8, 7, 5]  (root last)

def test_inorder_sorted():
    # InOrder on a BST must return values in ascending sorted order
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert inorder(root) == [1, 3, 4, 5, 6, 7, 8]

def test_preorder():
    # PreOrder visits root (5) then recurses left before right
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert preorder(root) == [5, 3, 1, 4, 7, 6, 8]

def test_postorder():
    # PostOrder visits children before the root; root (5) is always last
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert postorder(root) == [1, 4, 3, 6, 8, 7, 5]

def test_traversals_single_node():
    # All traversals of a single node return a list with that one value
    root = insert(None, 42)
    assert inorder(root)   == [42]
    assert preorder(root)  == [42]
    assert postorder(root) == [42]

def test_traversals_empty_tree():
    # All traversals of an empty tree return an empty list
    assert inorder(None)   == []
    assert preorder(None)  == []
    assert postorder(None) == []


# ─────────────────────────────────────────────
#  BFS
# ─────────────────────────────────────────────
#
#  BST from [5,3,7,1,4,6,8]:
#
#  Level 0: [5]
#  Level 1: [3, 7]
#  Level 2: [1, 4, 6, 8]

def test_bfs_level_order():
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert bfs(root) == [[5], [3, 7], [1, 4, 6, 8]]

def test_bfs_single_node():
    root = insert(None, 10)
    assert bfs(root) == [[10]]

def test_bfs_empty_tree():
    assert bfs(None) == []

def test_bfs_skewed_right():
    # [1,2,3,4] inserted in order produces a right-skewed chain
    # Each level contains exactly one node
    root = build_bst([1, 2, 3, 4])
    assert bfs(root) == [[1], [2], [3], [4]]

def test_bfs_returns_level_groups():
    # Two-level tree: root has left and right children
    # Level 0: [5], Level 1: [3, 8]
    root = build_bst([5, 3, 8])
    assert bfs(root) == [[5], [3, 8]]


# ─────────────────────────────────────────────
#  LEVEL ORDER FLAT LIST
# ─────────────────────────────────────────────

def test_level_order_flat_full_tree():
    # BST from [5,3,7,1,4,6,8] visits nodes top-to-bottom, left-to-right
    # Result is a single flat list: [5, 3, 7, 1, 4, 6, 8]
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert level_order_flat(root) == [5, 3, 7, 1, 4, 6, 8]

def test_level_order_flat_single_node():
    # A single node returns a list with just that value
    root = insert(None, 10)
    assert level_order_flat(root) == [10]

def test_level_order_flat_empty_tree():
    # An empty tree returns an empty list
    assert level_order_flat(None) == []

def test_level_order_flat_skewed_right():
    # [1,2,3,4] inserted in order — right-skewed chain
    # Level order visits each node top-to-bottom: [1, 2, 3, 4]
    root = build_bst([1, 2, 3, 4])
    assert level_order_flat(root) == [1, 2, 3, 4]

def test_level_order_flat_two_levels():
    # [5,3,8]: root 5, left 3, right 8 → flat order [5, 3, 8]
    root = build_bst([5, 3, 8])
    assert level_order_flat(root) == [5, 3, 8]

def test_level_order_flat_length_equals_node_count():
    # Flat list must contain exactly one entry per node
    values = [5, 3, 7, 1, 4, 6, 8]
    root = build_bst(values)
    assert len(level_order_flat(root)) == len(values)


# ─────────────────────────────────────────────
#  DFS
# ─────────────────────────────────────────────

def test_dfs_preorder_same_as_recursive():
    # Iterative DFS (pre-order) must match recursive preorder result
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert dfs(root) == preorder(root)

def test_dfs_single_node():
    root = insert(None, 7)
    assert dfs(root) == [7]

def test_dfs_empty_tree():
    assert dfs(None) == []

def test_dfs_skewed_left():
    # [4,3,2,1] inserted produces left-skewed chain
    # Pre-order DFS visits root first: [4, 3, 2, 1]
    root = build_bst([4, 3, 2, 1])
    assert dfs(root) == [4, 3, 2, 1]


# ─────────────────────────────────────────────
#  IS VALID BST
# ─────────────────────────────────────────────

def test_is_valid_bst_true():
    # Any BST built via insert() is guaranteed to be valid
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert is_valid_bst(root) is True

def test_is_valid_bst_empty_tree():
    # An empty tree is trivially a valid BST
    assert is_valid_bst(None) is True

def test_is_valid_bst_single_node():
    # A single node has no children; always valid
    root = TreeNode(42)
    assert is_valid_bst(root) is True

def test_is_valid_bst_right_child_too_large():
    # Manually wire: 5 → right=3 (3 < 5, violates BST property)
    root = make_tree(5, right=make_tree(3))
    assert is_valid_bst(root) is False

def test_is_valid_bst_left_child_too_large():
    # Manually wire: 5 → left=7 (7 > 5, violates BST property)
    root = make_tree(5, left=make_tree(7))
    assert is_valid_bst(root) is False

def test_is_valid_bst_ancestor_violation():
    # Classic trap: local children look fine but global range is violated
    #
    #      5
    #     / \
    #    1   6
    #       / \
    #      4   7    ← 4 < 5 violates the constraint that all right-subtree
    #                 values must be > 5
    root = make_tree(5,
        left=make_tree(1),
        right=make_tree(6,
            left=make_tree(4),   # 4 < 5 → invalid
            right=make_tree(7),
        )
    )
    assert is_valid_bst(root) is False

def test_is_valid_bst_equal_values_invalid():
    # BST property requires strict inequality; equal values are not valid
    #      5
    #     /
    #    5       ← duplicate in left subtree violates left < root
    root = make_tree(5, left=make_tree(5))
    assert is_valid_bst(root) is False


# ─────────────────────────────────────────────
#  PRINT TREE  (smoke test — just ensure no exceptions)
# ─────────────────────────────────────────────

def test_print_tree_no_exception():
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    print_tree(root)   # Should print without raising

def test_print_tree_empty_no_exception():
    print_tree(None)   # Should print "(empty tree)" without raising


# ─────────────────────────────────────────────
#  PRINT WRAPPERS
# ─────────────────────────────────────────────
#
#  BST from [5, 3, 7, 1, 4, 6, 8]:
#
#          5
#        /   \
#       3     7
#      / \   / \
#     1   4 6   8

def test_inorder_print_output():
    # InOrder of BST yields values in ascending sorted order
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert capture(inorder_print, root) == "[1, 3, 4, 5, 6, 7, 8]"

def test_inorder_print_empty():
    # Empty tree produces an empty list
    assert capture(inorder_print, None) == "[]"

def test_preorder_print_output():
    # PreOrder visits root (5) first, then recurses left before right
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert capture(preorder_print, root) == "[5, 3, 1, 4, 7, 6, 8]"

def test_preorder_print_single_node():
    # Single node; only that value is printed
    root = insert(None, 42)
    assert capture(preorder_print, root) == "[42]"

def test_postorder_print_output():
    # PostOrder visits all children before the root; root (5) is last
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert capture(postorder_print, root) == "[1, 4, 3, 6, 8, 7, 5]"

def test_postorder_print_empty():
    # Empty tree produces an empty list
    assert capture(postorder_print, None) == "[]"

def test_level_by_level_print_output():
    # Each level printed on its own line, no labels
    root = build_bst([5, 3, 7, 1, 4, 6, 8])
    assert capture(level_by_level_print, root) == "[5]\n[3, 7]\n[1, 4, 6, 8]"

def test_level_by_level_print_single_node():
    # Single node; one line with that value
    root = insert(None, 10)
    assert capture(level_by_level_print, root) == "[10]"

def test_level_by_level_print_empty():
    # Empty tree prints a single empty list
    assert capture(level_by_level_print, None) == "[]"


if __name__ == "__main__":
    # INSERT
    test_insert_into_empty_tree()
    test_insert_smaller_goes_left()
    test_insert_larger_goes_right()
    test_insert_multiple_maintains_bst()
    test_insert_duplicate_ignored()

    # FIND
    test_find_existing_value()
    test_find_root_value()
    test_find_missing_value()
    test_find_in_empty_tree()
    test_find_leaf_node()

    # DELETE
    test_delete_leaf_node()
    test_delete_node_with_one_child()
    test_delete_node_with_two_children()
    test_delete_root_node()
    test_delete_nonexistent_value()
    test_delete_from_empty_tree()
    test_delete_only_node()

    # TRAVERSALS
    test_inorder_sorted()
    test_preorder()
    test_postorder()
    test_traversals_single_node()
    test_traversals_empty_tree()

    # BFS
    test_bfs_level_order()
    test_bfs_single_node()
    test_bfs_empty_tree()
    test_bfs_skewed_right()
    test_bfs_returns_level_groups()

    # LEVEL ORDER FLAT
    test_level_order_flat_full_tree()
    test_level_order_flat_single_node()
    test_level_order_flat_empty_tree()
    test_level_order_flat_skewed_right()
    test_level_order_flat_two_levels()
    test_level_order_flat_length_equals_node_count()

    # DFS
    test_dfs_preorder_same_as_recursive()
    test_dfs_single_node()
    test_dfs_empty_tree()
    test_dfs_skewed_left()

    # IS VALID BST
    test_is_valid_bst_true()
    test_is_valid_bst_empty_tree()
    test_is_valid_bst_single_node()
    test_is_valid_bst_right_child_too_large()
    test_is_valid_bst_left_child_too_large()
    test_is_valid_bst_ancestor_violation()
    test_is_valid_bst_equal_values_invalid()

    # PRINT TREE
    test_print_tree_no_exception()
    test_print_tree_empty_no_exception()

    # PRINT WRAPPERS
    test_inorder_print_output()
    test_inorder_print_empty()
    test_preorder_print_output()
    test_preorder_print_single_node()
    test_postorder_print_output()
    test_postorder_print_empty()
    test_level_by_level_print_output()
    test_level_by_level_print_single_node()
    test_level_by_level_print_empty()

    print("\nAll tests passed.")
