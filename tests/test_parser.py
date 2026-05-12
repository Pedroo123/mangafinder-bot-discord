import pytest
from utils.parser import parse_search_query

def test_parse_query_no_flags():
    query = "One Piece"
    normalized, subreddit = parse_search_query(query)
    assert normalized == "One Piece"
    assert subreddit == "manga"

def test_parse_query_with_subreddit_flag_long():
    query = "One Piece --subreddit anime"
    normalized, subreddit = parse_search_query(query)
    assert normalized == "One Piece"
    assert subreddit == "anime"

def test_parse_query_with_subreddit_flag_short():
    query = "One Piece -s manhwa"
    normalized, subreddit = parse_search_query(query)
    assert normalized == "One Piece"
    assert subreddit == "manhwa"

def test_parse_query_flag_in_middle():
    query = "One --subreddit manhwa Piece"
    normalized, subreddit = parse_search_query(query)
    assert normalized == "One Piece"
    assert subreddit == "manhwa"

def test_parse_query_empty_after_flag():
    query = "--subreddit manga"
    normalized, subreddit = parse_search_query(query)
    assert normalized == ""
    assert subreddit == "manga"

def test_parse_query_with_extra_spaces():
    query = "  One   Piece   -s   manga  "
    normalized, subreddit = parse_search_query(query)
    assert normalized == "One Piece"
    assert subreddit == "manga"
