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

    def put(self, element):
        self.queue_list += [element]
