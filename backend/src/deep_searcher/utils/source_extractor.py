import re

def extract_sources_from_report(report_text: str) -> list[str]:
    """Uses regex to find all unique source URLs cited in the report text."""
    # Regex to find [Source: URL] or [Source: URL, Page: X]
    # It captures the URL part.
    pattern = r'\[Source:\s*(https?://[^\s,\]]+)'
    matches = re.findall(pattern, report_text)
    
    # Return a de-duplicated list while preserving order
    unique_sources = list(dict.fromkeys(matches))
    return unique_sources