# src/deep_searcher/utils/sanitizers.py
import re
import hashlib

def sanitize_for_collection_name(name: str) -> str:
    """
    Sanitizes a string to be a valid ChromaDB collection name.

    ChromaDB collection names must:
    - be between 3 and 63 characters long.
    - start and end with an alphanumeric character.
    - not contain two consecutive dots.
    - only contain alphanumeric characters, underscores, and dots.

    Args:
        name: The input string (e.g., a brand name).

    Returns:
        A sanitized string that is a valid collection name.
    """
    if not isinstance(name, str) or not name:
        raise ValueError("Input name must be a non-empty string.")

    # Replace all non-alphanumeric characters (except dots) with an underscore
    sanitized = re.sub(r'[^a-zA-Z0-9.]+', '_', name.lower())

    # Remove leading/trailing underscores or dots
    sanitized = sanitized.strip('_.')

    # Replace consecutive dots with a single dot
    sanitized = re.sub(r'\.\.+', '.', sanitized)

    # Truncate to a max length of 50 to leave room for prefixes/suffixes
    sanitized = sanitized[:50]

    # Ensure the name is at least 3 characters long
    if len(sanitized) < 3:
        # If too short, append a hash of the original name to ensure uniqueness and length
        hash_suffix = hashlib.md5(name.encode()).hexdigest()[:8]
        sanitized = f"{sanitized}_{hash_suffix}"[:63] # Ensure it doesn't exceed max length

    # Final check for start/end characters
    if not sanitized[0].isalnum():
        sanitized = 'c' + sanitized[1:]
    if not sanitized[-1].isalnum():
        sanitized = sanitized[:-1] + 'c'

    return sanitized