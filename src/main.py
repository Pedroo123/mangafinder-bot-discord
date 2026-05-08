import discord
import logging
import sys
from discord.ext import commands
from config import Config
from service.reddit_service import RedditService
from ui.embed_factory import format_manga_embed
from utils.parser import parse_search_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Validate configuration on startup
Config.validate()

# Intents are required for discord.py >= 2.0
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Lazily initialized reddit service
_reddit_service = None

def get_reddit_service():
    global _reddit_service
    if _reddit_service is None:
        _reddit_service = RedditService()
    return _reddit_service

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info('------')

@bot.command(name='search')
async def search(ctx, *, query: str):
    """
    Searches for a manga. Defaults to r/manga.
    Usage: !search <query> [--subreddit <name> | -s <name>]
    Example: !search One Piece
             !search Berserk --subreddit manga
             !search Naruto -s anime
    """
    query, subreddit_name = parse_search_query(query)

    if not query:
        await ctx.send("Please provide a search term. Usage: !search <query> [--subreddit <name>]")
        return

    await ctx.send(f"Searching for '{query}' in r/{subreddit_name}...")

    try:
        service = get_reddit_service()
        result = await service.search_subreddit(subreddit_name, query, limit=10)
        posts = result.get('posts', [])

        if not posts:
            await ctx.send("No results found.")
            return

        for post in posts:
            embed = format_manga_embed(post)
            await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !search <query>")
    else:
        logger.error(f"Error: {error}")

@bot.event
async def close():
    """
    Closes the reddit service when the bot closes.
    """
    if _reddit_service:
        await _reddit_service.close()
    await super(commands.Bot, bot).close()

if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    finally:
        # Proper cleanup if not handled by event loop
        import asyncio
        if _reddit_service:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(_reddit_service.close())
                else:
                    loop.run_until_complete(_reddit_service.close())
            except Exception:
                pass
