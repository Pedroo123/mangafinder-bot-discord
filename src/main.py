import discord
import logging
import asyncio
import re
from discord.ext import commands
from config import Config
from service.reddit_service import RedditService
from ui.embed_factory import format_manga_embed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MangaBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reddit_service = None

    def get_reddit_service(self):
        if self._reddit_service is None:
            self._reddit_service = RedditService()
        return self._reddit_service

    async def close(self):
        """
        Properly closes the reddit service when the bot is closed.
        """
        if self._reddit_service:
            logger.info("Closing reddit service...")
            await self._reddit_service.close()
        await super().close()

# Validate configuration on startup
Config.validate()

# Intents are required for discord.py >= 2.0
intents = discord.Intents.default()
intents.message_content = True

bot = MangaBot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info('------')

@bot.command(name='search')
async def search(ctx, *, arg: str):
    """
    Searches for a manga in a subreddit.
    Usage: !search <query> [--subreddit subreddit_name]
    Example: !search One Piece
             !search Naruto --subreddit animemes
    Note: Defaults to r/manga. Use --subreddit or -s to change.
    """
    # Parse the argument for --subreddit or -s
    subreddit = 'manga'
    query = arg

    # Match --subreddit <name> or -s <name> at the end or anywhere
    match = re.search(r'(?:\s|^)(?:--subreddit|-s)\s+([^\s]+)', arg)
    if match:
        subreddit = match.group(1)
        # Remove the flag and the value from the query
        query = arg.replace(match.group(0), '').strip()

    if not query:
        await ctx.send("Please provide a search query.")
        return

    await ctx.send(f"Searching for '{query}' in r/{subreddit}...")

    try:
        service = bot.get_reddit_service()
        result = await service.search_subreddit(subreddit, query, limit=10)
        posts = result.get('posts', [])

        if not posts:
            await ctx.send("No results found.")
            return

        embeds = [format_manga_embed(post) for post in posts]

        # Discord allows up to 10 embeds per message
        await ctx.send(embeds=embeds)

    except Exception as e:
        logger.exception(f"Error during search command: {e}")
        await ctx.send("An error occurred while searching. Please try again later.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !search <query> [--subreddit subreddit_name]")
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore unknown commands
    else:
        logger.error(f"Discord command error: {error}")

if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
