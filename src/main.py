import discord
import logging
from discord.ext import commands
from config import Config
from service.reddit_service import RedditService
from ui.embed_factory import format_manga_embed
from utils.parser import parse_search_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MangaFinderBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self._reddit_service = None

    def get_reddit_service(self):
        if self._reddit_service is None:
            self._reddit_service = RedditService()
        return self._reddit_service

    async def close(self):
        logger.info("Closing bot and cleaning up resources...")
        if self._reddit_service:
            await self._reddit_service.close()
        await super().close()

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')

bot = MangaFinderBot()

@bot.command(name='search')
async def search(ctx, *, full_query: str):
    """
    Searches for a manga.
    Usage: !search <query> [--subreddit <name> | -s <name>]
    Example: !search One Piece --subreddit manga
    """
    query, subreddit_name = parse_search_query(full_query)

    if not query:
        await ctx.send("Please provide a search query.")
        return

    await ctx.send(f"Searching for '{query}' in r/{subreddit_name}...")

    try:
        service = bot.get_reddit_service()
        # Retrieve more than 1 if needed, but we limit to 10 for Discord embeds
        result = await service.search_subreddit(subreddit_name, query, limit=10)
        posts = result.get('posts', [])

        if not posts:
            await ctx.send(f"No results found for '{query}' in r/{subreddit_name}.")
            return

        embeds = [format_manga_embed(post) for post in posts]

        # Discord allows up to 10 embeds per message
        for i in range(0, len(embeds), 10):
            await ctx.send(embeds=embeds[i:i+10])

    except Exception as e:
        logger.exception("Error during search command")
        await ctx.send(f"An error occurred: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !search <query> [--subreddit <name>]")
    else:
        logger.error(f"Command error: {error}")

if __name__ == "__main__":
    Config.validate()
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
