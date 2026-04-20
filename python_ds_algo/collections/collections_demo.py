import collections

def collection_samples():
    # 1. namedtuple: Defining a clean 'Task' object
    Task = collections.namedtuple('Task', ['id', 'priority', 'name'])
    
    # 2. deque: A queue to hold tasks (O(1) pops from the left)
    queue = collections.deque([
        Task(1, 'High', 'Fix Bug'),
        Task(2, 'Low', 'Refactor'),
        Task(3, 'High', 'Write Tests')
    ])

    # 3. defaultdict: Grouping task names by their priority level
    priority_groups = collections.defaultdict(list)
    
    # 4. Counter: Tracking how many times each priority appears
    priority_counts = collections.Counter()

    # 5. OrderedDict: Storing finished tasks in the exact order they completed
    completed_log = collections.OrderedDict()

    print("--- Processing Tasks ---")
    while queue:
        # Fast removal from the front of the queue
        current_task = queue.popleft()
        
        # Log priority frequency and group the task
        priority_counts[current_task.priority] += 1
        priority_groups[current_task.priority].append(current_task.name)
        
        # Simulate completion
        completed_log[current_task.id] = "Success"
        print(f"Finished: {current_task.name}")

    print("\n--- Summary Stats ---")
    print(f"Priority Counts: {dict(priority_counts)}")
    print(f"Priority Groups: {dict(priority_groups)}")
    print(f"Completion Order: {list(completed_log.keys())}")

if __name__ == "__main__":
    collection_samples()
