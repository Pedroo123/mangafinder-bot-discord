import re
from typing import Tuple, Optional

def parse_search_query(query: str) -> Tuple[str, str]:
    """
    Parses the search query for flags like --subreddit or -s.
    Returns (cleaned_query, subreddit_name).
    Defaults to 'manga' if no subreddit is specified.
    """
    # Regex to find --subreddit <name> or -s <name>
    subreddit_match = re.search(r'(?:--subreddit|-s)\s+([^\s]+)', query)

    subreddit_name = 'manga'
    if subreddit_match:
        subreddit_name = subreddit_match.group(1)
        # Remove the flag and the subreddit name from the query
        query = query.replace(subreddit_match.group(0), '')

    # Clean up whitespace
    query = re.sub(r'\s+', ' ', query).strip()

    return query, subreddit_name
