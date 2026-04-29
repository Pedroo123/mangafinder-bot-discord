import os
import discord
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from service.reddit_service import RedditService

load_dotenv()

# Intents are required for discord.py >= 2.0
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Deferred initialization to allow testing without credentials
reddit_service = None

def get_reddit_service():
    global reddit_service
    if reddit_service is None:
        reddit_service = RedditService()
    return reddit_service

def format_manga_embed(post: dict) -> discord.Embed:
    """
    Formats a Reddit post into a professional Discord Embed card.
    Strictly includes: Title, Date, Front Page (image), and Link.
    """
    title = post.get('title', 'No Title')
    url = post.get('permalink', post.get('url', ''))
    created_utc = post.get('created_utc')

    date_str = "Unknown Date"
    if created_utc:
        # Professional date format: October 14, 2023
        date_str = datetime.fromtimestamp(created_utc).strftime('%B %d, %Y')

    embed = discord.Embed(
        title=title[:256],
        url=url,
        description=f"**Date Published:** {date_str}",
        color=discord.Color.blue() # Clean blue color for professional look
    )

    image_url = post.get('thumbnail')
    if image_url and image_url.startswith('http'):
        embed.set_image(url=image_url)

    embed.set_footer(text=f"Reddit | r/{post.get('subreddit', 'manga')}")

    # Ensuring the link is also explicitly mentioned if needed,
    # though the title is already a link.
    # embed.add_field(name="Link", value=f"[Click here to view]({url})", inline=False)

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
        service = get_reddit_service()
        result = await service.search_subreddit(subreddit_name, query, limit=5)
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
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not found in environment.")
    else:
        bot.run(token)
