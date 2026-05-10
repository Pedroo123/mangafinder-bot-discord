import pytest
from utils.parser import parse_search_query

def test_parse_search_query_no_flags():
    query, subreddit = parse_search_query("One Piece")
    assert query == "One Piece"
    assert subreddit == "manga"

def test_parse_search_query_with_subreddit_flag():
    query, subreddit = parse_search_query("One Piece --subreddit mangaplus")
    assert query == "One Piece"
    assert subreddit == "mangaplus"

def test_parse_search_query_with_short_subreddit_flag():
    query, subreddit = parse_search_query("-s mangaplus Chainsaw Man")
    assert query == "Chainsaw Man"
    assert subreddit == "mangaplus"

def test_parse_search_query_empty():
    query, subreddit = parse_search_query("")
    assert query == ""
    assert subreddit == "manga"

def test_parse_search_query_only_flag():
    query, subreddit = parse_search_query("--subreddit mangaplus")
    assert query == ""
    assert subreddit == "mangaplus"
