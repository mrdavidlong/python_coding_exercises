import pytest
from linked_list import ListNode
from linked_list_sort import sort_linked_list

IMPLEMENTATIONS = [sort_linked_list]

@pytest.fixture(params=IMPLEMENTATIONS)
def fn(request):
    return request.param

def make_list(vals):
    """Build a linked list from a Python list of values."""
    if not vals:
        return None
    head = ListNode(vals[0])
    curr = head
    for v in vals[1:]:
        curr.next = ListNode(v)
        curr = curr.next
    return head

def list_to_vals(head):
    """Convert linked list to Python list of values."""
    vals = []
    while head:
        vals.append(head.val)
        head = head.next
    return vals

def test_unsorted(fn):
    # [4,2,3,1] is unsorted; merge sort should produce [1,2,3,4]
    assert list_to_vals(fn(make_list([4, 2, 3, 1]))) == [1, 2, 3, 4]

def test_already_sorted(fn):
    # [1,2,3] is already sorted; result should remain [1,2,3]
    assert list_to_vals(fn(make_list([1, 2, 3]))) == [1, 2, 3]

def test_single_node(fn):
    # Single node is trivially sorted; returns the same node
    assert list_to_vals(fn(make_list([1]))) == [1]

def test_empty_list(fn):
    # None (empty list) returns None
    assert fn(None) is None

def test_two_nodes(fn):
    # [2,1] out of order; sorted result is [1,2]
    assert list_to_vals(fn(make_list([2, 1]))) == [1, 2]

if __name__ == "__main__":
    for fn in IMPLEMENTATIONS:
        test_unsorted(fn)
        test_already_sorted(fn)
        test_single_node(fn)
        test_empty_list(fn)
        test_two_nodes(fn)
    print("All tests passed.")
