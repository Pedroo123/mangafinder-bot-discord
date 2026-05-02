import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from config import Config
from service.reddit_service import RedditService

# Validate configuration at runtime
def run_bot():
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    # Intents are required for discord.py >= 2.0
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='!', intents=intents)
    reddit_service = RedditService()

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
        await ctx.send(f"Searching for '{query}' in r/{subreddit_name}...")

        try:
            result = await reddit_service.search_subreddit(subreddit_name, query, limit=5)
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
            await ctx.send("Missing arguments. Usage: !search <subreddit> <query>")
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(f"Error: {error}")

    try:
        bot.run(Config.DISCORD_TOKEN)
    finally:
        # PRAW close is async, but bot.run is sync.
        if not asyncio.get_event_loop().is_closed():
            asyncio.run(reddit_service.close())

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
        # Format: October 24, 2023
        date_str = datetime.fromtimestamp(created_utc).strftime('%B %d, %Y')

    embed = discord.Embed(
        title=title[:256],
        url=url,
        color=discord.Color.blue()
    )

    embed.add_field(name="Date", value=date_str, inline=False)

    image_url = post.get('thumbnail')
    if image_url and image_url.startswith('http'):
        embed.set_image(url=image_url)

    # Footer for context
    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

    return embed

if __name__ == "__main__":
    run_bot()
