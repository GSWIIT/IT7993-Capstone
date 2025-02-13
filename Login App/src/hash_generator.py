import hashlib
import json
import os

NAMES_FILE = "names.json"
HASH_FILE = "hashes.json"

def generate_name_hash(name):
    """Generate SHA-256 hash from a user's name."""
    return hashlib.sha256(name.encode()).hexdigest()

def load_json(filename):
    """Load JSON file safely."""
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in {filename}, starting fresh.")
    return {}

def save_json(filename, data):
    """Save dictionary to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_and_store_hashes():
    """Generate and store a single hash for each unique user name."""
    names_data = load_json(NAMES_FILE)
    hash_data = load_json(HASH_FILE)

    unique_names = set(names_data.values())  # Get unique names

    for name in unique_names:
        if name not in hash_data:  # Only generate hash if it doesn’t exist
            hash_data[name] = generate_name_hash(name)
            print(f"Generated hash for {name}: {hash_data[name]}")

    save_json(HASH_FILE, hash_data)

if __name__ == "__main__":
    generate_and_store_hashes()
    print("Hashes updated successfully!")
