import pytest
from src.main import format_manga_embed
import discord

def test_format_manga_embed_basic():
    post = {
        "title": "One Piece Chapter 1000",
        "permalink": "https://reddit.com/r/manga/comments/xyz",
        "created_utc": 1609459200, # 2021-01-01
        "subreddit": "manga",
        "thumbnail": "https://example.com/image.jpg"
    }

    embed = format_manga_embed(post)

    assert embed.title == "One Piece Chapter 1000"
    assert embed.url == "https://reddit.com/r/manga/comments/xyz"
    assert embed.fields[0].name == "Date"
    assert embed.fields[0].value == "January 01, 2021"
    assert embed.image.url == "https://example.com/image.jpg"
    assert embed.footer.text == "Source: r/manga"

def test_format_manga_embed_missing_data():
    post = {}
    embed = format_manga_embed(post)

    assert embed.title == "No Title"
    assert embed.fields[0].value == "Unknown Date"
    assert embed.image.url is None

def test_format_manga_embed_long_title():
    post = {
        "title": "A" * 300,
        "created_utc": 1609459200
    }
    embed = format_manga_embed(post)
    assert len(embed.title) == 256
