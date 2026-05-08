import pytest
from utils.parser import parse_search_query

def test_parse_query_no_flags():
    query = "One Piece"
    q, s = parse_search_query(query)
    assert q == "One Piece"
    assert s == "manga"

def test_parse_query_with_subreddit_flag():
    query = "Berserk --subreddit manga"
    q, s = parse_search_query(query)
    assert q == "Berserk"
    assert s == "manga"

def test_parse_query_with_short_flag():
    query = "Naruto -s anime"
    q, s = parse_search_query(query)
    assert q == "Naruto"
    assert s == "anime"

def test_parse_query_flag_in_middle():
    query = "One -s anime Piece"
    q, s = parse_search_query(query)
    assert q == "One Piece"
    assert s == "anime"

def test_parse_query_multi_word_query():
    query = "My Hero Academia --subreddit BokuNoHeroAcademia"
    q, s = parse_search_query(query)
    assert q == "My Hero Academia"
    assert s == "BokuNoHeroAcademia"

def test_parse_query_only_flag():
    query = "--subreddit manga"
    q, s = parse_search_query(query)
    assert q == ""
    assert s == "manga"
