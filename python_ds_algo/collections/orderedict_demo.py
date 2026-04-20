from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key not in self.cache:
            print(f"MISS: '{key}' not in cache")
            return None
        
        # Move to end to mark as "Recently Used"
        self.cache.move_to_end(key)
        print(f"HIT:  '{key}' retrieved from cache")
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            # Update existing value and move to end
            self.cache.move_to_end(key)
        
        self.cache[key] = value
        
        # Evict oldest if we exceed capacity
        if len(self.cache) > self.capacity:
            oldest_key, _ = self.cache.popitem(last=False)
            print(f"EVICT: Cache full, removed '{oldest_key}'")

# --- Demo: Storing User Profiles ---
user_cache = LRUCache(2)

# 1. Store some users
user_cache.put("user_101", {"name": "Alice", "role": "Admin"})
user_cache.put("user_102", {"name": "Bob", "role": "User"})

# 2. Access Alice (making her the most recent)
alice = user_cache.get("user_101")
print(f"Data: {alice['name']}")

# 3. Add a third user (this will evict Bob because Alice was recently accessed)
user_cache.put("user_103", {"name": "Charlie", "role": "Guest"})

# 4. Try to get Bob (should be a MISS)
bob = user_cache.get("user_102")

print(f"\nFinal Cache Keys (Oldest to Newest): {list(user_cache.cache.keys())}")
