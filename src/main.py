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
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class MangaFinderBot(commands.Bot):
    def __init__(self):
        Config.validate()
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self._reddit_service = None

    async def get_reddit_service(self):
        if self._reddit_service is None:
            self._reddit_service = RedditService()
        return self._reddit_service

    async def setup_hook(self):
        logger.info(f"Setting up bot: {self.user}")

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')

    async def close(self):
        if self._reddit_service:
            logger.info("Closing Reddit service...")
            await self._reddit_service.close()
        await super().close()

bot = MangaFinderBot()

@bot.command(name='search')
async def search(ctx, *, query: str):
    """
    Searches for a manga.
    Usage: !search <query> [--subreddit <name>]
    Example: !search One Piece
    """
    query, subreddit_name = parse_search_query(query)

    if not query:
        await ctx.send("Please provide a search query.")
        return

    await ctx.send(f"Searching for '{query}' in r/{subreddit_name}...")

    try:
        service = await bot.get_reddit_service()
        result = await service.search_subreddit(subreddit_name, query, limit=5)
        posts = result.get('posts', [])

        if not posts:
            await ctx.send("No results found.")
            return

        for post in posts:
            embed = format_manga_embed(post)
            await ctx.send(embed=embed)

    except Exception as e:
        logger.exception("Error during search command")
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !search <query>")
    else:
        logger.error(f"Command error: {error}")

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
