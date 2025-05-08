import hashlib
import json
import os
from typing import List, Tuple


def compute_hashes(resource_list: List[Tuple[str, str, str, str]]) -> List[str]:
    """
    Computes a list of SHA-256 hashes for given resources.

    Args:
        resource_list (list): A list of tuples (course_id, _, name, url).

    Returns:
        list: A list of hexadecimal hash strings.
    """
    return [
        hashlib.sha256((course_id + name + url).encode()).hexdigest()
        for course_id, _, name, url in resource_list
    ]


def load_hashes(path: str = "data/hashes.json") -> List[str]:
    """
    Loads previously saved resource hashes from a JSON file.

    Args:
        path (str): Path to the JSON file.

    Returns:
        list: A list of previously computed hash strings.
    """
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []


def save_hashes(hashes: List[str], path: str = "data/hashes.json") -> None:
    """
    Saves computed hashes to a JSON file.

    Args:
        hashes (list): A list of hash strings to save.
        path (str): Path to the JSON file.
    """
    with open(path, "w") as f:
        json.dump(hashes, f, indent=2)


def hash_single(course_id: str, name: str, url: str) -> str:
    """
    Computes a SHA-256 hash for a single resource.

    Args:
        course_id (str): The course identifier.
        name (str): The resource name.
        url (str): The resource URL.

    Returns:
        str: A hexadecimal SHA-256 hash string.
    """
    return hashlib.sha256((course_id + name + url).encode()).hexdigest()