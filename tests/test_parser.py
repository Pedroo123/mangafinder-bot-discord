import pytest
from utils.parser import parse_search_query

def test_parse_query_default():
    query, subreddit = parse_search_query("One Piece")
    assert query == "One Piece"
    assert subreddit == "manga"

def test_parse_query_with_subreddit_flag():
    query, subreddit = parse_search_query("One Piece --subreddit anime")
    assert query == "One Piece"
    assert subreddit == "anime"

def test_parse_query_with_short_flag():
    query, subreddit = parse_search_query("-s manhwa Solo Leveling")
    assert query == "Solo Leveling"
    assert subreddit == "manhwa"

def test_parse_query_with_extra_spaces():
    query, subreddit = parse_search_query("   One Piece   --subreddit    manga   ")
    assert query == "One Piece"
    assert subreddit == "manga"

def test_parse_query_empty_after_flag():
    # Should handle it gracefully, though Discord might not send it
    query, subreddit = parse_search_query("--subreddit manga")
    assert query == ""
    assert subreddit == "manga"
