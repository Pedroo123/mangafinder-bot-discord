import os
import discord
from discord.ext import commands
from datetime import datetime
from config import config
from service.reddit_service import RedditService

# Validate config at startup
try:
    config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    exit(1)

# Intents are required for discord.py >= 2.0
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Lazily initialized Reddit service
_reddit_service = None

def get_reddit_service():
    global _reddit_service
    if _reddit_service is None:
        _reddit_service = RedditService()
    return _reddit_service

def format_manga_embed(post: dict) -> discord.Embed:
    """
    Formats a Reddit post into a Discord Embed card.
    Includes: Title, Date, Front Page (image), and Link.
    """
    title = post.get('title', 'No Title')
    url = post.get('permalink', post.get('url', ''))
    created_utc = post.get('created_utc')

    date_str = "Unknown Date"
    if created_utc:
        date_str = datetime.fromtimestamp(created_utc).strftime('%B %d, %Y')

    embed = discord.Embed(
        title=title[:256],
        url=url,
        color=discord.Color.blue(),
        timestamp=datetime.fromtimestamp(created_utc) if created_utc else None
    )

    embed.add_field(name="Published", value=date_str, inline=True)
    embed.add_field(name="Subreddit", value=f"r/{post.get('subreddit', 'unknown')}", inline=True)

    image_url = post.get('thumbnail')
    if image_url and image_url.startswith('http'):
        embed.set_image(url=image_url)

    embed.set_footer(text="MangaFinder Bot")

    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command(name='search')
async def search(ctx, subreddit_name: str, *, query: str):
    """
    Searches for a manga in a specific subreddit.
    Usage: !search <subreddit> <manga_name>
    """
    async with ctx.typing():
        try:
            service = get_reddit_service()
            result = await service.search_subreddit(subreddit_name, query, limit=3)
            posts = result.get('posts', [])

            if not posts:
                await ctx.send(f"No results found for '{query}' in r/{subreddit_name}.")
                return

            for post in posts:
                embed = format_manga_embed(post)
                await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"An error occurred while searching: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: `!search <subreddit> <query>`")
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore unknown commands
    else:
        print(f"Error: {error}")
        await ctx.send("An unexpected error occurred.")

@bot.event
async def on_close():
    if _reddit_service:
        await _reddit_service.close()

async def close_services():
    if _reddit_service:
        await _reddit_service.close()

if __name__ == "__main__":
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Bot execution failed: {e}")
    finally:
        # PRAW needs a loop to close its session
        import asyncio
        if _reddit_service:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(_reddit_service.close())
