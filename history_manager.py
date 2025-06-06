from typing import List


class HistoryManager:
    """
    A history manager that stores items in a list.
    """

    def __init__(self):
        self.history: List[str] = []
        self.current_index = -1

    def add(self, item):
        """
        Add an item to the history.
        """
        if len(self.history) > 0:
            last_item = self.history[-1]
            if last_item == item:
                return
        if self.current_index < len(self.history) - 1:
            del self.history[self.current_index + 1 :]
        self.history.append(item)
        self.current_index = len(self.history) - 1

    def get(self, index):
        """
        Get an item by index, allowing for negative indexing.
        """
        if 0 <= index < len(self.history):
            return self.history[index]
        raise IndexError("Index out of range")

    def clear(self):
        """
        Clear the history.
        """
        self.history.clear()

    def back(self):
        """
        Move back in the history if possible.

        raises IndexError if there is no previous item.
        """
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        raise IndexError("No previous item in history")

    def forward(self):
        """
        Move forward in the history if possible.

        raises IndexError if there is no next item.
        """
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        raise IndexError("No next item in history")

    def __contains__(self, item):
        """
        Check if an item is in the history.

        :Usage:
        >>> "http://example.com/page1" in history_manager
        True
        """
        return item in self.history

    def __len__(self):
        """
        Get the number of items in the history.

        :Usage:
        >>> len(history_manager)
        """
        return len(self.history)

    def __getitem__(self, index):
        """
        Get an item by index, allowing for negative indexing.

        :Usage:
        >>> history_manager[0]
        >>> history_manager[-1]
        """
        return self.get(index)

    def __str__(self):
        return self.history.__str__()


if __name__ == "__main__":
    history_manager = HistoryManager()
    history_manager.add("http://example.com/page1")
    history_manager.add("http://example.com/page2")
    history_manager.add("http://example.com/page2")
    print(history_manager.get(0))
    print(history_manager[0])
    print(history_manager.back())
    print(history_manager.forward())
    print(len(history_manager))
    print(history_manager)
