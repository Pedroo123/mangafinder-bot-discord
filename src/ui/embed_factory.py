import discord
from datetime import datetime

def format_manga_embed(post: dict) -> discord.Embed:
    """
    Formats a Reddit post into a Discord Embed card.
    Strictly includes: Title, Date, Front Page (image), and Link.
    """
    title = post.get('title', 'No Title')
    url = post.get('permalink', post.get('url', ''))
    created_utc = post.get('created_utc')
    date_str = "Unknown Date"
    if created_utc:
        # User requested specific date format in memory: %B %d, %Y
        date_str = datetime.fromtimestamp(created_utc).strftime('%B %d, %Y')

    embed = discord.Embed(
        title=title[:256],
        url=url,
        color=discord.Color.blue()
    )

    embed.add_field(name="Date", value=date_str, inline=False)

    image_url = post.get('thumbnail')
    if image_url:
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

    return embed
