'''
Assume :
    1. Cache with deletion option.
    2. Cache with priority_promotion
    The lastly updated user_role or role_max_request_hit is highly likely to be accessed, 
    so if there is an existing key, delete it and insert the new one as freshest in the queue.


'''


from loguru import logger

class Node:
    def __init__(self, key : str, value : str,prev=None, next=None) -> None:
        self.value=value
        self.key=key
        self.prev=prev
        self.next=next

class CustomQueue:
    def __init__(self,max_size : int =10) -> None:
        self.max_size=max_size
        self.first_node=None
        self.last_node=None
        self.num_of_elements=0
    
    def push(self,key,val, existing_node=None):
        if self.is_full():
            if existing_node:
                self.delete(existing_node)
                new_node=Node(key,val, None, None)
                self.last_node.next=new_node
                new_node.prev=self.last_node
                self.last_node=new_node
                self.num_of_elements+=1
                return key,new_node
            else:
                first_node,first_node_key=self.first_node,self.first_node.key
                self.first_node=self.first_node.next
                self.first_node.prev=None
                del first_node
                new_node=Node(key,val, None, None)
                self.last_node.next=new_node
                new_node.prev=self.last_node
                self.last_node=new_node
                return first_node_key, new_node
        else:
            if existing_node:
                self.delete(existing_node)
            new_node=Node(key,val, None, None)
            if self.num_of_elements==0:
                self.first_node=new_node
                self.last_node=new_node
            else:
                self.last_node.next=new_node
                new_node.prev=self.last_node
                self.last_node=new_node
            self.num_of_elements+=1
            if existing_node: return key,new_node
            else: return None, new_node
    def is_full(self):
        return self.num_of_elements==self.max_size

    def delete(self,node : Node):
        if self.first_node==self.last_node==node:
            del node
            self.first_node=self.last_node=None
        elif self.first_node==node:
            first_node=self.first_node
            self.first_node=self.first_node.next
            self.first_node.prev=None
            del first_node
        elif self.last_node==node:
            last_node=self.last_node
            self.last_node=self.last_node.prev
            self.last_node.next=None
            del last_node
        else:
            node.prev.next=node.next
            node.next.prev=node.prev
            del node
        self.num_of_elements-=1

class Cache:
    def __init__(self,max_size : int=10) -> None:
        self.custom_queue=CustomQueue(max_size)
        self.dict=dict()
        
    def push(self, key, value):
        key_to_be_deleted,new_node=self.custom_queue.push(key,value,existing_node=self.dict.get(key,None))
        if key_to_be_deleted:
            try:
                self.dict.pop(key_to_be_deleted)
            except KeyError:
                assert False, "Inconsistency found in cache"  # Assuming key is always present in cache
        self.dict[key]=new_node
        
    def get(self, key):
        if key in self.dict:
            return self.dict.get(key).value
        return None
    
    def delete(self, key):
        if key in self.dict:
            self.custom_queue.delete(self.dict[key])
            self.dict.pop(key)
        else:
            raise KeyError(f"Key '{key}' not found in cache.")



def test_cache_with_priority_promotion():
    # Create a cache with a max size of 3
    cache = Cache(max_size=3)

    # Push abstract keys and values into the cache
    cache.push("key1", "value1")
    cache.push("key2", "value2")
    cache.push("key3", "value3")

    # Verify the cache is full
    print(f"Cache is full: {cache.custom_queue.is_full()}")  # Expected: True

    # Get and print all items
    print(f"key1: {cache.get('key1')}")  # Expected: value1
    print(f"key2: {cache.get('key2')}")  # Expected: value2
    print(f"key3: {cache.get('key3')}")  # Expected: value3

    # Update an existing key ("key1") to promote it
    cache.push("key1", "new_value1")  # "key1" should become the freshest in the queue
    print(f"key1 updated to: {cache.get('key1')}")  # Expected: new_value1

    # Push a new key and check eviction
    cache.push("key4", "value4")  # This should evict "key2" since it's the least recently updated
    try:
        print(f"key2: {cache.get('key2')}")
    except AttributeError:
        print("key2 has been evicted.")  # Expected: key2 has been evicted

    # Verify remaining keys
    print(f"key1: {cache.get('key1')}")  # Expected: new_value1
    print(f"key3: {cache.get('key3')}")  # Expected: value3
    print(f"key4: {cache.get('key4')}")  # Expected: value4

    # Promote another existing key ("key3")
    cache.push("key3", "new_value3")  # "key3" should become the freshest
    print(f"key3 updated to: {cache.get('key3')}")  # Expected: new_value3

    # Push another new key and verify eviction of the least recently updated key
    cache.push("key5", "value5")  # This should evict "key1"
    try:
        print(f"key1: {cache.get('key1')}")
    except AttributeError:
        print("key1 has been evicted.")  # Expected: key1 has been evicted

    # Verify final cache state
    print(f"key3: {cache.get('key3')}")  # Expected: new_value3
    print(f"key4: {cache.get('key4')}")  # Expected: value4
    print(f"key5: {cache.get('key5')}")  # Expected: value5

if __name__ == "__main__":
    # Run the test function
    test_cache_with_priority_promotion()


