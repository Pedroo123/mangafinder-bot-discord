import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/0.1 by Brankksss")

    @classmethod
    def validate(cls):
        required_vars = {
            "DISCORD_TOKEN": "Discord Bot Token",
            "REDDIT_CLIENT_ID": "Reddit API Client ID",
            "REDDIT_CLIENT_SECRET": "Reddit API Client Secret",
            "REDDIT_USERNAME": "Reddit Username",
            "REDDIT_PASSWORD": "Reddit Password"
        }
        missing = [friendly_name for var, friendly_name in required_vars.items() if not getattr(cls, var)]
        if missing:
            # When running in Azure, these should be set in the Container App environment
            error_msg = "Configuration Error: The following required environment variables are missing:\n"
            for item in missing:
                error_msg += f"- {item}\n"
            error_msg += "Please check your .env file or Azure environment settings."
            raise ValueError(error_msg)
