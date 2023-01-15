# HashTable class using chaining.
class ChainingHashTable:
    # Constructor with optional initial capacity parameter.
    # Assigns all buckets with an empty list.
    def __init__(self, initial_capacity=10):
        # initialize the hash table with empty bucket list entries.
        self.table = []
        for i in range(initial_capacity):
            self.table.append([])
      
    # Inserts a new item into the hash table.
    def insert(self, item):
        # get the bucket list where this item will go.
        bucket = None

        if 'packageId' in item.keys():
            bucket = hash(item['packageId']) % len(self.table)
            
        elif 'locationId' in item.keys():
            bucket = hash(item['locationId']) % len(self.table)

        bucket_list = self.table[bucket]

        # insert the item to the end of the bucket list.
        bucket_list.append(item)
         
    # Searches for an item with matching key in the hash table.
    # Returns the item if found, or None if not found.
    def search(self, key):
        # get the bucket list where this key would be.
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # search for the key in the bucket list
        for item in bucket_list:
            if ('packageId' in item.keys() and key == item['packageId']) or \
                ('locationId' in item.keys() and key == item['locationId']):
                return item

        # return none if key not found
        return None

    # Removes an item with matching key from the hash table.
    def remove(self, key):
        # get the bucket list where this item will be removed from.
        bucket = hash(key) % len(self.table)
        bucket_list = self.table[bucket]

        # remove the item from the bucket list if it is present.
        for item in bucket_list:
            if ('packageId' in item.keys() and key == item['packageId']) or \
                ('locationId' in item.keys() and key == item['locationId']):
                bucket_list.remove(item)