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
reddit_service = RedditService()

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
        # Using a cleaner date format
        date_str = datetime.fromtimestamp(created_utc).strftime('%B %d, %Y')

    embed = discord.Embed(
        title=title[:256],
        url=url,
        color=discord.Color.orange() # Reddit-ish color
    )

    embed.add_field(name="Date", value=date_str, inline=False)

    thumbnail = post.get('thumbnail')
    if thumbnail:
        embed.set_image(url=thumbnail)

    # Adding a footer with the link as well for clarity
    embed.set_footer(text=f"Source: r/{post.get('subreddit', 'reddit')}")

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
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("Error: DISCORD_TOKEN not found in environment.")
    else:
        bot.run(token)
