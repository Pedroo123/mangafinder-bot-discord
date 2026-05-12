import re
from typing import Tuple

def parse_search_query(query: str, default_subreddit: str = "manga") -> Tuple[str, str]:
    """
    Parses a search query to extract an optional subreddit flag.
    Supports --subreddit <name> or -s <name>.
    Returns (clean_query, subreddit_name).
    """
    subreddit = default_subreddit

    # Match --subreddit <name> or -s <name>
    # Handle possible spaces and different positions
    pattern = r'(?:\s|^)(?:--subreddit|-s)\s+([^\s]+)'
    match = re.search(pattern, query)

    if match:
        subreddit = match.group(1)
        # Remove the flag and the value from the query
        query = re.sub(pattern, '', query).strip()

    # Further clean up multiple spaces
    query = re.sub(r'\s+', ' ', query).strip()

    return query, subreddit
