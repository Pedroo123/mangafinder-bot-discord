import pytest
from ui.embed_factory import format_manga_embed
import discord

def test_format_manga_embed_basic():
    post = {
        'title': 'Test Manga',
        'permalink': 'https://reddit.com/r/manga/test',
        'created_utc': 1600000000,
        'thumbnail': 'https://example.com/image.jpg',
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    assert isinstance(embed, discord.Embed)
    assert embed.title == 'Test Manga'
    assert embed.url == 'https://reddit.com/r/manga/test'
    assert embed.fields[0].name == 'Date'
    # 1600000000 is September 13, 2020
    assert embed.fields[0].value == 'September 13, 2020'
    assert embed.image.url == 'https://example.com/image.jpg'
    assert embed.footer.text == 'Source: r/manga'

def test_format_manga_embed_missing_image():
    post = {
        'title': 'Test Manga No Image',
        'permalink': 'https://reddit.com/r/manga/test',
        'created_utc': 1600000000,
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    assert embed.image.url is None

def test_format_manga_embed_missing_date():
    post = {
        'title': 'Test Manga No Date',
        'permalink': 'https://reddit.com/r/manga/test',
        'subreddit': 'manga'
    }

    embed = format_manga_embed(post)

    assert embed.fields[0].value == 'Unknown Date'
