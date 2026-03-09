class CallbackDeque:
    def __init__(self, maxlen, callback=lambda x: None):
        self.deque = []
        self.maxlen = maxlen
        self.callback = callback

    def append(self, item, call_callback=True, args=(), kwargs={}):
        if len(self.deque) >= self.maxlen:
            removed_item = self.deque.pop(0)
            if call_callback:
                self.callback(removed_item, *args, **kwargs)
        self.deque.append(item)

    def __len__(self):
        return len(self.deque)

    def __getitem__(self, index):
        return self.deque[index]

    def clear(self, call_callback=True, args=(), kwargs={}):
        while self.deque:
            item = self.deque.pop(0)
            if call_callback:
                self.callback(item, *args, **kwargs)

    def setCallback(self, callback):
        self.callback = callback

    def getAll(self):
        return self.deque[:]  # return a shallow copy

    def __repr__(self) -> str:
        return f"CallbackDeque({self.deque})"

    def __str__(self) -> str:
        return str(self.deque)
