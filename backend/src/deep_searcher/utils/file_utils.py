# src/deep_searcher/utils/file_utils.py
from pathlib import Path

def load_prompt(file_path: str) -> str:
    """Loads a prompt from a file."""
    try:
        with open(Path(file_path), "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file not found at: {file_path}")