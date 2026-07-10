from Stacks.stack import Stack


def test_push_and_pop():
    # Push 1, 2, 3; pop should return them in LIFO order: 3, 2, 1
    s = Stack()
    s.push(1)
    s.push(2)
    s.push(3)
    assert s.pop() == 3
    assert s.pop() == 2
    assert s.pop() == 1


def test_peek_does_not_remove():
    # peek returns the top element but leaves it on the stack; pop still returns it
    s = Stack()
    s.push(10)
    s.push(20)
    assert s.peek() == 20
    assert s.pop() == 20


def test_pop_empty_returns_none():
    # Popping an empty stack returns None rather than raising an error
    s = Stack()
    assert s.pop() is None


def test_peek_empty_returns_none():
    # Peeking an empty stack returns None rather than raising an error
    s = Stack()
    assert s.peek() is None


def test_is_empty():
    # is_empty is True on a new stack, False after a push, True again after popping all elements
    s = Stack()
    assert s.is_empty()
    s.push(1)
    assert not s.is_empty()
    s.pop()
    assert s.is_empty()


def test_size():
    # size tracks the number of elements correctly across pushes and pops
    s = Stack()
    assert s.size() == 0
    s.push(1)
    s.push(2)
    assert s.size() == 2
    s.pop()
    assert s.size() == 1


def test_interleaved_push_pop():
    # Interleaving pushes and pops should always reflect LIFO order at each step
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.pop() == 2
    s.push(3)
    assert s.pop() == 3
    assert s.pop() == 1
    assert s.pop() is None


def test_single_element():
    # A stack with one element should peek and pop that element, then be empty
    s = Stack()
    s.push(42)
    assert s.peek() == 42
    assert s.pop() == 42
    assert s.is_empty()


if __name__ == "__main__":
    test_push_and_pop()
    test_peek_does_not_remove()
    test_pop_empty_returns_none()
    test_peek_empty_returns_none()
    test_is_empty()
    test_size()
    test_interleaved_push_pop()
    test_single_element()
    print("All tests passed.")
