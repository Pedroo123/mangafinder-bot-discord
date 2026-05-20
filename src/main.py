import discord
import logging
import asyncio
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
        # Validate configuration on startup
        Config.validate()

        # Intents are required for discord.py >= 2.0
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix='!', intents=intents)
        self._reddit_service = None

    def get_reddit_service(self):
        if self._reddit_service is None:
            self._reddit_service = RedditService()
        return self._reddit_service

    async def on_ready(self):
        logger.info(f'Logged in as {self.user.name} (ID: {self.user.id})')
        logger.info('------')

    async def close(self):
        """
        Closes the reddit service when the bot closes.
        """
        logger.info("Shutting down bot and cleaning up resources...")
        if self._reddit_service:
            try:
                await self._reddit_service.close()
                logger.info("Reddit service closed successfully.")
            except Exception as e:
                logger.error(f"Error closing reddit service: {e}")
        await super().close()

bot = MangaFinderBot()

@bot.command(name='search')
async def search(ctx, *, query: str):
    """
    Searches for a manga.
    Usage: !search <query> [--subreddit <name> | -s <name>]
    Example: !search One Piece --subreddit manga
    """
    normalized_query, subreddit_name = parse_search_query(query)

    if not normalized_query:
        await ctx.send("Please provide a search query.")
        return

    logger.info(f"User {ctx.author} searched for '{normalized_query}' in r/{subreddit_name}")
    await ctx.send(f"Searching for '{normalized_query}' in r/{subreddit_name}...")

    try:
        service = bot.get_reddit_service()
        # Explicitly wrap the search in a timeout to ensure it doesn't hang
        result = await asyncio.wait_for(
            service.search_subreddit(subreddit_name, normalized_query, limit=10),
            timeout=15.0
        )
        posts = result.get('posts', [])

        if not posts:
            logger.info(f"No results found for '{normalized_query}'")
            await ctx.send(f"No results found for '{normalized_query}' in r/{subreddit_name}.")
            return

        # Discord allows up to 10 embeds per message.
        # We'll batch them in groups of 5 for better readability.
        batch_size = 5
        for i in range(0, len(posts), batch_size):
            batch = posts[i:i + batch_size]
            embeds = [format_manga_embed(post) for post in batch]
            await ctx.send(embeds=embeds)

    except asyncio.TimeoutError:
        logger.error("Reddit search timed out.")
        await ctx.send("Search timed out. Reddit might be slow right now.")
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "forbidden" in error_msg.lower():
            await ctx.send(f"Error: {error_msg}")
        else:
            logger.error(f"Error during search command: {e}", exc_info=True)
            await ctx.send("An unexpected error occurred while searching. Please try again later.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Usage: !search <query>")
    elif isinstance(error, commands.CommandNotFound):
        pass # Ignore unknown commands
    else:
        logger.error(f"Command error: {error}")

if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
