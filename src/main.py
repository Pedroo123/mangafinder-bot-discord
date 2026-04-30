import discord
from discord.ext import commands
from datetime import datetime
from config import Config
from service.reddit_service import RedditService

# Validate configuration on startup
try:
    Config.validate()
except ValueError as e:
    print(f"Configuration Error: {e}")
    exit(1)

# Intents are required for discord.py >= 2.0
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
reddit_service = RedditService()

def format_manga_embed(post: dict) -> discord.Embed:
    """
    Formats a Reddit post into a Discord Embed card.
    Strictly includes: Title, Date, Front Page (image), and Link.
    """
    title = post.get('title', 'No Title')
    url = post.get('permalink', post.get('url', ''))
    created_utc = post.get('created_utc')

    # Format date as requested: %B %d, %Y
    date_str = "Unknown Date"
    if created_utc:
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

    # Required: Link for redirect is already in the title and can be added as a field or footer
    # We'll add it as a field for extra visibility if requested, but title URL is standard.
    embed.add_field(name="Link", value=f"[Click here to read]({url})", inline=False)

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
    else:
        print(f"Error: {error}")

if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    finally:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
             loop.create_task(reddit_service.close())
        else:
             asyncio.run(reddit_service.close())
