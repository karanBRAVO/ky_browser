def load_json(file_path):
    """Load a JSON file and return its content."""
    import json

    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None
