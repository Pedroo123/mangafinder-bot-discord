import pytest
from utils.parser import parse_search_query

def test_parse_query_no_flags():
    query = "One Piece"
    cleaned, subreddit = parse_search_query(query)
    assert cleaned == "One Piece"
    assert subreddit == "manga"

def test_parse_query_with_subreddit_flag():
    query = "Solo Leveling --subreddit manhwa"
    cleaned, subreddit = parse_search_query(query)
    assert cleaned == "Solo Leveling"
    assert subreddit == "manhwa"

def test_parse_query_with_short_flag():
    query = "Kingdom -s Seinen"
    cleaned, subreddit = parse_search_query(query)
    assert cleaned == "Kingdom"
    assert subreddit == "Seinen"

def test_parse_query_with_flag_in_middle():
    query = "Search --subreddit manga query"
    cleaned, subreddit = parse_search_query(query)
    assert cleaned == "Search query"
    assert subreddit == "manga"

def test_parse_query_empty():
    query = ""
    cleaned, subreddit = parse_search_query(query)
    assert cleaned == ""
    assert subreddit == "manga"

def test_parse_query_only_flag():
    query = "--subreddit manga"
    cleaned, subreddit = parse_search_query(query)
    assert cleaned == ""
    assert subreddit == "manga"
