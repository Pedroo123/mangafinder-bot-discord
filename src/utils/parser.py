import re

def parse_search_query(query: str):
    """
    Parses a search query to extract optional subreddit flags.
    Returns a tuple of (cleaned_query, subreddit_name).
    """
    subreddit_name = 'manga'

    # Simple regex to extract --subreddit or -s flag and its value
    # Matches: --subreddit name or -s name
    subreddit_match = re.search(r'(?:--subreddit|-s)\s+([^\s]+)', query)

    if subreddit_match:
        subreddit_name = subreddit_match.group(1)
        # Remove the flag and subreddit name from the search query and clean up whitespace
        query = re.sub(r'(?:--subreddit|-s)\s+[^\s]+', '', query)
        query = re.sub(r'\s+', ' ', query).strip()
    else:
        query = query.strip()

    return query, subreddit_name
