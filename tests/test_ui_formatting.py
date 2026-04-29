import pytest
import discord
from datetime import datetime
from main import format_manga_embed

def test_format_manga_embed_success():
    post = {
        "title": "Test Manga Title",
        "permalink": "https://reddit.com/r/manga/test",
        "created_utc": 1600000000,
        "thumbnail": "https://example.com/image.jpg",
        "subreddit": "manga"
    }

    embed = format_manga_embed(post)

    assert embed.title == "Test Manga Title"
    assert embed.url == "https://reddit.com/r/manga/test"
    assert "September 13, 2020" in embed.description
    assert embed.image.url == "https://example.com/image.jpg"
    assert embed.footer.text == "Reddit | r/manga"

def test_format_manga_embed_missing_image():
    post = {
        "title": "Test Manga Title",
        "permalink": "https://reddit.com/r/manga/test",
        "created_utc": 1600000000,
        "thumbnail": None,
        "subreddit": "manga"
    }

    embed = format_manga_embed(post)

    assert embed.title == "Test Manga Title"
    assert not embed.image.url

def test_format_manga_embed_invalid_created_utc():
    post = {
        "title": "Test Manga Title",
        "permalink": "https://reddit.com/r/manga/test",
        "created_utc": None,
        "thumbnail": "https://example.com/image.jpg",
        "subreddit": "manga"
    }

    embed = format_manga_embed(post)

    assert "Unknown Date" in embed.description
