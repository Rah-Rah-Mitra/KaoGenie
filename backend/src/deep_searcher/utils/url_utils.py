# src/deep_searcher/utils/url_utils.py
import logging
import re

logger = logging.getLogger(__name__)

def normalize_url(url: str) -> str:
    """
    Cleans and normalizes a URL to fix common issues found during web crawling.
    - Replaces all backslashes with forward slashes.
    - Corrects malformed schemes like 'https:/www...' to 'https://www...'.

    Args:
        url: The raw URL string to be cleaned.

    Returns:
        A cleaned, more compliant URL string. Returns an empty string if input is invalid.
    """
    if not isinstance(url, str) or not url.strip():
        return ""

    original_url = url
    
    # 1. Replace all backslashes with forward slashes
    cleaned_url = url.strip().replace('\\', '/')

    # 2. Fix incorrect scheme format (e.g., "https:/www.site.com" -> "https://www.site.com")
    # This regex correctly inserts a second slash if it's missing after the protocol.
    cleaned_url = re.sub(r'^(https?:)/([^/])', r'\1//\2', cleaned_url)

    if cleaned_url != original_url:
        logger.debug(f"Normalized URL: '{original_url}' -> '{cleaned_url}'")
        
    return cleaned_url