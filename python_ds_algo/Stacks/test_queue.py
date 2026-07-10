from Stacks.queue import Queue


def test_fifo_order():
    # Enqueue 1, 2, 3; dequeue should return them in the same FIFO order
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    q.enqueue(3)
    assert q.dequeue() == 1
    assert q.dequeue() == 2
    assert q.dequeue() == 3


def test_peek_does_not_remove():
    # peek returns the front element but leaves it in the queue; dequeue still returns it afterward
    q = Queue()
    q.enqueue(1)
    q.enqueue(2)
    assert q.peek() == 1
    assert q.dequeue() == 1


def test_dequeue_empty_returns_none():
    # Dequeuing an empty queue returns None rather than raising an error
    q = Queue()
    assert q.dequeue() is None


def test_peek_empty_returns_none():
    # Peeking an empty queue returns None rather than raising an error
    q = Queue()
    assert q.peek() is None


def test_is_empty():
    # is_empty is True on a new queue, False after an enqueue, True again after dequeuing all
    q = Queue()
    assert q.is_empty()
    q.enqueue(1)
    assert not q.is_empty()
    q.dequeue()
    assert q.is_empty()


def test_size():
    # size tracks the number of elements correctly across enqueues and dequeues
    q = Queue()
    assert q.size() == 0
    q.enqueue(1)
    q.enqueue(2)
    assert q.size() == 2
    q.dequeue()
    assert q.size() == 1


def test_interleaved_enqueue_dequeue():
    # Interleaving enqueue and dequeue should still respect FIFO ordering at each step
    q = Queue()
    q.enqueue(10)
    q.enqueue(20)
    assert q.dequeue() == 10
    q.enqueue(30)
    assert q.dequeue() == 20
    assert q.dequeue() == 30
    assert q.dequeue() is None


def test_single_element():
    # A queue with one element should peek and dequeue that element, then be empty
    q = Queue()
    q.enqueue(99)
    assert q.peek() == 99
    assert q.dequeue() == 99
    assert q.is_empty()


if __name__ == "__main__":
    test_fifo_order()
    test_peek_does_not_remove()
    test_dequeue_empty_returns_none()
    test_peek_empty_returns_none()
    test_is_empty()
    test_size()
    test_interleaved_enqueue_dequeue()
    test_single_element()
    print("All tests passed.")
