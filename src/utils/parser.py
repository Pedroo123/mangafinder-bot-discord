import re
from typing import Tuple, Optional

def parse_search_query(query: str) -> Tuple[str, str]:
    """
    Parses the search query to extract an optional subreddit flag.
    Supported flags: --subreddit <name>, -s <name>

    Returns:
        Tuple[str, str]: (normalized_query, subreddit_name)
    """
    subreddit_name = 'manga'  # Default

    # Pattern to match --subreddit <name> or -s <name>
    # Supports names with underscores and alphanumeric characters
    flag_pattern = r'(?:\s+|^)(?:--subreddit|-s)\s+([a-zA-Z0-9_]+)(?:\s+|$)'

    match = re.search(flag_pattern, query)
    if match:
        subreddit_name = match.group(1)
        # Remove the flag and its value from the query
        normalized_query = re.sub(flag_pattern, ' ', query).strip()
    else:
        normalized_query = query.strip()

    # Ensure multi-word queries are preserved and extra spaces removed
    normalized_query = ' '.join(normalized_query.split())

    return normalized_query, subreddit_name
