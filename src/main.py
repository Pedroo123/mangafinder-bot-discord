import discord
from discord.ext import commands
from config import Config
from service.reddit_service import RedditService
from ui.embed_factory import format_manga_embed
from utils.parser import parse_search_query
import logging
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration on startup
Config.validate()

class MangaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self._reddit_service = None

    async def get_reddit_service(self):
        if self._reddit_service is None:
            self._reddit_service = RedditService()
        return self._reddit_service

    async def close(self):
        if self._reddit_service:
            await self._reddit_service.close()
        await super().close()

bot = MangaBot()

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    logger.info('------')

@bot.command(name='search')
async def search(ctx, *, query: str):
    """
    Searches for a manga.
    Usage: !search <query> [--subreddit <name> | -s <name>]
    Example: !search One Piece --subreddit mangaplus
    """
    query, subreddit_name = parse_search_query(query)

    if not query:
        await ctx.send("Please provide a search term.")
        return

    await ctx.send(f"Searching for '{query}' in r/{subreddit_name}...")

    try:
        service = await bot.get_reddit_service()
        # limit=10 because Discord allows up to 10 embeds in a single message
        result = await service.search_subreddit(subreddit_name, query, limit=10)
        posts = result.get('posts', [])

        if not posts:
            await ctx.send("No results found.")
            return

        embeds = [format_manga_embed(post) for post in posts]

        # Send all embeds in a single message (Discord limit is 10)
        await ctx.send(embeds=embeds)

    except Exception as e:
        logger.exception("Error during search command")
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !search <query> [--subreddit <name>]")
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore unknown commands
    else:
        logger.error(f"Command error: {error}")

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
