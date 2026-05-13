import pytest
import discord
from datetime import datetime, timezone
from ui.embed_factory import format_manga_embed

def test_format_manga_embed_full_data():
    post = {
        'title': 'Test Manga',
        'permalink': 'https://reddit.com/r/manga/comments/123',
        'created_utc': 1672531200,  # 2023-01-01 00:00:00 UTC
        'thumbnail': 'https://example.com/image.jpg',
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    assert embed.title == 'Test Manga'
    assert embed.url == 'https://reddit.com/r/manga/comments/123'
    assert embed.timestamp == datetime.fromtimestamp(1672531200, tz=timezone.utc)
    assert embed.image.url == 'https://example.com/image.jpg'
    assert embed.footer.text == 'Source: r/manga'

    # Check for the Date field
    date_field = next(f for f in embed.fields if f.name == "Date")
    assert date_field.value == 'January 01, 2023'

def test_format_manga_embed_missing_date():
    post = {
        'title': 'Test Manga',
        'url': 'https://example.com',
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    assert embed.title == 'Test Manga'
    assert embed.timestamp is None
    date_field = next(f for f in embed.fields if f.name == "Date")
    assert date_field.value == 'Unknown Date'

def test_format_manga_embed_no_thumbnail():
    post = {
        'title': 'Test Manga',
        'created_utc': 1672531200,
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    # discord.py Embed image.url returns None if not set,
    # and discord.utils.MISSING or Empty is not an attribute of Embed.
    assert embed.image.url is None

def test_format_manga_embed_dual_links():
    post = {
        'title': 'Test Manga',
        'url': 'https://mangadex.org/chapter/123',
        'permalink': 'https://reddit.com/r/manga/comments/123',
        'created_utc': 1672531200,
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    assert embed.url == 'https://mangadex.org/chapter/123'
    link_field = next(f for f in embed.fields if f.name == "Link")
    assert "[Content](https://mangadex.org/chapter/123)" in link_field.value
    assert "[Reddit](https://reddit.com/r/manga/comments/123)" in link_field.value
