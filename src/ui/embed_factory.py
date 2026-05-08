import discord
from datetime import datetime, timezone

def format_manga_embed(post: dict) -> discord.Embed:
    """
    Formats a Reddit post into a Discord Embed card.
    Strictly includes: Title, Date, Front Page (image), and Link.
    """
    title = post.get('title', 'No Title')
    # Use permalink if available, otherwise fallback to url
    url = post.get('permalink', post.get('url', ''))
    created_utc = post.get('created_utc')

    embed = discord.Embed(
        title=title[:256],
        url=url,
        color=discord.Color.blue()
    )

    if created_utc:
        dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)
        date_str = dt.strftime('%B %d, %Y')
        embed.add_field(name="Date", value=date_str, inline=False)
        # Also set the timestamp for the embed's own date display for better UI integration
        embed.timestamp = dt
    else:
        embed.add_field(name="Date", value="Unknown Date", inline=False)

    image_url = post.get('thumbnail')
    # Robust check: Ensure it is a valid absolute http(s) URL
    if image_url and isinstance(image_url, str) and image_url.startswith('http'):
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

    return embed
