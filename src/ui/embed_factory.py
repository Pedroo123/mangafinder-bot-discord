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

    # Use permalink if available, otherwise fallback to url
    # Ensure URL is also clean
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
        embed.add_field(name="Date", value=date_str, inline=True)
        # Also set the timestamp for the embed's own date display
        embed.timestamp = dt
    else:
        embed.add_field(name="Date", value="Unknown Date", inline=True)

    # Adding a dedicated Link field as per requirement 3
    if url:
        embed.add_field(name="Link", value=f"[Click here to view]({url})", inline=True)

    image_url = post.get('thumbnail')
    # For Discord embeds, we only set the image if it's a valid http(s) link.
    if image_url and image_url.startswith('http'):
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

    return embed
