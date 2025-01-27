
'''
Assume :
    1. elements are not deleted from the Cache.


'''

class Node:
    def __init__(self,value : str,next=None) -> None:
        self.value = value
        self.next = next

class CustomQueue:
    def __init__(self,max_size =10) -> None:
        self.max_size = max_size
        self.first_node = None
        self.last_node = None
        self.num_of_elements = 0
    
    def push(self, key):
        if self.num_of_elements < self.max_size:
            new_node= Node(key, None)
            if self.num_of_elements == 0:
                self.first_node=new_node
                self.last_node=new_node
                self.num_of_elements+=1
            else:
                self.last_node.next=new_node
                self.last_node=self.last_node.next
                self.num_of_elements+=1
            return None
        else:
            to_be_removed_key=self.first_node.value
            node_to_be_removed=self.first_node
            self.first_node=self.first_node.next
            del node_to_be_removed
            new_node= Node(key, None)
            self.last_node.next=new_node
            self.last_node=self.last_node.next
            return to_be_removed_key
    
    def is_full(self):
        return self.num_of_elements == self.max_size
    
class Cache:
    def __init__(self, max_size= 10):
        self.custom_queue = CustomQueue(max_size)
        self.dict = dict()
    def push(self, key, value):
        to_be_deleted_key=self.custom_queue.push(key)
        if to_be_deleted_key:
            try:
                self.dict.pop(to_be_deleted_key)
            except KeyError:
                assert False, "Inconsistency found in cache"  # Assuming key is always present in cache
        self.dict[key] = value
    def get(self, key):
        return self.dict[key]
    def num_of_elements(self):
        return self.custom_queue.num_of_elements
    def is_full(self):
        return self.custom_queue.is_full()


def test_cache():
    cache = Cache(max_size=3)  # Create a cache with max size 3
    
    # Push items into the cache
    cache.push("key1", "value1")
    cache.push("key2", "value2")
    cache.push("key3", "value3")
    
    # Check if the cache is full
    print(f"Cache is full: {cache.is_full()}")  # Expected: True, as cache max size is 3 and there are 3 elements
    
    # Get items from the cache
    print(f"key1: {cache.get('key1')}")  # Expected: value1
    print(f"key2: {cache.get('key2')}")  # Expected: value2
    print(f"key3: {cache.get('key3')}")  # Expected: value3
    
    # Push another item into the cache to check eviction
    cache.push("key4", "value4")  # This should evict "key1"
    
    # Check if "key1" is evicted
    try:
        print(f"key1: {cache.get('key1')}")
    except KeyError:
        print("key1 has been evicted.")  # Expected: key1 has been evicted

    # Get remaining items in the cache
    print(f"key2: {cache.get('key2')}")  # Expected: value2
    print(f"key3: {cache.get('key3')}")  # Expected: value3
    print(f"key4: {cache.get('key4')}")  # Expected: value4
    
    # Push another item and check eviction again
    cache.push("key5", "value5")  # This should evict "key2"
    
    # Check if "key2" is evicted
    try:
        print(f"key2: {cache.get('key2')}")
    except KeyError:
        print("key2 has been evicted.")  # Expected: key2 has been evicted
    
    # Get remaining items
    print(f"key3: {cache.get('key3')}")  # Expected: value3
    print(f"key4: {cache.get('key4')}")  # Expected: value4
    print(f"key5: {cache.get('key5')}")  # Expected: value5
    
if __name__ == "__main__":
    # Run the test function
    test_cache()
    '''
    expected output:
        Cache is full: True
        key1: value1
        key2: value2
        key3: value3
        key1 has been evicted.
        key2: value2
        key3: value3
        key4: value4
        key2 has been evicted.
        key3: value3
        key4: value4
        key5: value5
        
    
    returned output:
        Cache is full: True
        key1: value1
        key2: value2
        key3: value3
        key1 has been evicted.
        key2: value2
        key3: value3
        key4: value4
        key2 has been evicted.
        key3: value3
        key4: value4
        key5: value5

    So working as expected.
    
    
    '''
