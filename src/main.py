import discord
from discord.ext import commands
from datetime import datetime
from config import Config
from service.reddit_service import RedditService

# Validate configuration on startup
Config.validate()

# Intents are required for discord.py >= 2.0
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Delay service initialization until bot is starting or needed
reddit_service = None

def get_reddit_service():
    global reddit_service
    if reddit_service is None:
        reddit_service = RedditService()
    return reddit_service

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
        color=discord.Color.blue()
    )

    embed.add_field(name="Date", value=date_str, inline=False)

    image_url = post.get('thumbnail')
    if image_url:
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command(name='search')
async def search(ctx, *, query: str):
    """
    Searches for a manga. Defaults to r/manga.
    Usage: !search <manga_name>
    Optional: !search r/subreddit <manga_name>
    """
    subreddit_name = "manga"
    search_query = query

    if query.startswith("r/"):
        parts = query.split(" ", 1)
        if len(parts) > 1:
            subreddit_name = parts[0].replace("r/", "")
            search_query = parts[1]
        else:
            await ctx.send("Please provide a search query after the subreddit.")
            return

    await ctx.send(f"Searching for '{search_query}' in r/{subreddit_name}...")

    try:
        service = get_reddit_service()
        result = await service.search_subreddit(subreddit_name, search_query, limit=5)
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
        await ctx.send("Missing arguments. Usage: !search <query> or !search r/subreddit <query>")
    else:
        print(f"Error: {error}")

if __name__ == "__main__":
    try:
        bot.run(Config.DISCORD_TOKEN)
    finally:
        if reddit_service:
            import asyncio
            loop = asyncio.get_event_loop()
            loop.run_until_complete(reddit_service.close())
