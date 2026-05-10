import re
from typing import Tuple, Optional

def parse_search_query(query: str) -> Tuple[str, str]:
    """
    Parses the search query to extract optional flags.
    Supported flags: --subreddit <name>, -s <name>

    Returns:
        Tuple[str, str]: (search_terms, subreddit_name)
    """
    # Regex to find --subreddit or -s followed by a word
    subreddit_pattern = r'(?:--subreddit|-s)\s+([^\s]+)'

    match = re.search(subreddit_pattern, query)

    subreddit_name = 'manga'  # Default
    if match:
        subreddit_name = match.group(1)
        # Remove the flag and its value from the query
        query = re.sub(subreddit_pattern, '', query)

    # Clean up whitespace
    query = ' '.join(query.split())

    return query, subreddit_name
