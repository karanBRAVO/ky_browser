import os
import json


class BookmarksManager:
    """
    A class to manage bookmarks.
    """

    BOOKMARK_FILE = "bookmarks.json"

    def __init__(self):
        self.exists = True
        if not os.path.exists(self.BOOKMARK_FILE):
            try:
                with open(self.BOOKMARK_FILE, "w") as file:
                    json.dump({}, file, indent=2)
            except Exception as e:
                print(f"An error occurred while creating the bookmark file: {e}")
                self.exists = False

    def save_bookmark(self, title: str, url: str):
        """
        Save a bookmark with the given title and URL.
        """
        if not self.exists:
            return
        bookmarks = dict(self.load_bookmarks())
        if title in bookmarks:
            return
        new_bookmark = {title: url}
        try:
            bookmarks.update(new_bookmark)
            with open(self.BOOKMARK_FILE, "w") as file:
                json.dump(bookmarks, file, indent=2)
        except FileNotFoundError:
            print("Bookmark file not found, creating a new one.")
        except json.JSONDecodeError:
            print("Bookmark file is corrupted, creating a new one.")
        except Exception as e:
            print(f"An error occurred while reading bookmarks: {e}")

    def load_bookmarks(self):
        """
        Load all saved bookmarks.
        """
        if not self.exists:
            return {}
        try:
            with open(self.BOOKMARK_FILE, "r") as file:
                bookmarks = json.load(file)
                return dict(bookmarks)
        except FileNotFoundError:
            print("Bookmark file not found.")
            return {}
        except json.JSONDecodeError:
            print("Bookmark file is corrupted.")
            return {}
        except Exception as e:
            print(f"An error occurred while loading bookmarks: {e}")
            return {}


if __name__ == "__main__":
    manager = BookmarksManager()
    # Example usage
    manager.save_bookmark("Example", "https://example.com")
    bookmarks = manager.load_bookmarks()
    print(bookmarks)
