import discord
import html
from datetime import datetime, timezone

def format_manga_embed(post: dict) -> discord.Embed:
    """
    Formats a Reddit post into a Discord Embed card.
    Strictly includes: Title, Date, Front Page (image), and Link.
    """
    # HTML unescape title just in case the API returns escaped characters
    title = html.unescape(post.get('title', 'No Title'))

    # external_url is where the content is (e.g. MangaDex, imgur)
    external_url = post.get('url')
    # reddit_url is the discussion link
    reddit_url = post.get('permalink')

    # Main URL for the title should be the content if possible
    main_url = external_url if external_url else reddit_url
    created_utc = post.get('created_utc')

    embed = discord.Embed(
        title=title[:256],
        url=main_url,
        color=discord.Color.blue()
    )

    if created_utc:
        dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
        date_str = dt.strftime('%B %d, %Y')
        embed.add_field(name="Date", value=date_str, inline=True)
        embed.timestamp = dt
    else:
        embed.add_field(name="Date", value="Unknown Date", inline=True)

    # Link field as per requirement 3
    if external_url and reddit_url and external_url != reddit_url:
        embed.add_field(name="Link", value=f"[Content]({external_url}) | [Reddit]({reddit_url})", inline=True)
    elif main_url:
        embed.add_field(name="Link", value=f"[View Post]({main_url})", inline=True)

    image_url = post.get('thumbnail')
    if image_url and image_url.startswith('http'):
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

    return embed
