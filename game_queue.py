class GameQueue:
    def __init__(self, grid):
        self.queue_list = []  # Somehow the python queue class hangs

    def reset(self):
        self.queue_list = []

    def get(self):
        if self.queue_list:
            element = self.queue_list[0]
            self.queue_list = self.queue_list[1:]
            return element

    def insert(self, element):
        '''Add element to beginning of the queue'''
        self.queue_list = [element] + self.queue_list

    def push(self, element):
        '''Add element to the end of the queue'''
        self.queue_list += [element]

    def __len__(self):
        return len(self.queue_list)

    def __bool__(self):
        return self.queue_list != []
