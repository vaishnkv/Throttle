
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
                existing_node.value=val
                return None, existing_node
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
                existing_node.value=val
                return None, existing_node
            else:
                new_node=Node(key,val, None, None)
                if self.num_of_elements==0:
                    self.first_node=new_node
                    self.last_node=new_node
                else:
                    self.last_node.next=new_node
                    new_node.prev=self.last_node
                    self.last_node=new_node
                self.num_of_elements+=1
                return None, new_node
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
    def get_stats(self):
        if len(self.dict)==0:
            logger.info("Cache is empty.")
        for key in self.dict.keys():
            logger.info(f"Key: {key}, Value: {self.dict[key].value}")
    def delete(self, key):
        if key in self.dict:
            self.custom_queue.delete(self.dict[key])
            self.dict.pop(key)
        else:
            raise KeyError(f"Key '{key}' not found in cache.")
