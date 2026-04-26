import os
import asyncpraw
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class RedditService:
    def __init__(self):
        self.reddit = asyncpraw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            username=os.getenv("REDDIT_USERNAME"),
            password=os.getenv("REDDIT_PASSWORD"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "mangafinder-bot/0.1 by Brankksss")
        )

    async def search_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int = 25,
        sort: str = "new",
        after: Optional[str] = None
    ) -> Dict[str, Any]:
        if not subreddit_name:
            raise ValueError("subreddit_name is required")
        if not query:
            raise ValueError("query is required")

        subreddit = await self.reddit.subreddit(subreddit_name)

        # AsyncPRAW search doesn't have an 'after' parameter directly in search()
        # but we can use the listing generator.
        # restrict_sr=True is equivalent to searching within the subreddit.
        search_results = subreddit.search(
            query,
            sort=sort,
            limit=limit,
            time_filter="all",
            params={"after": after} if after else None
        )

        posts = []
        last_fullname = None

        async for submission in search_results:
            # Replicating the mapping logic from TS
            post = {
                "id": submission.id,
                "title": submission.title,
                "url": submission.url,
                "permalink": f"https://reddit.com{submission.permalink}" if submission.permalink else None,
                "author": str(submission.author) if submission.author else None,
                "created_utc": submission.created_utc,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "subreddit": str(submission.subreddit),
                "thumbnail": self._get_best_image(submission)
            }
            posts.append(post)
            last_fullname = submission.name

        return {
            "posts": posts,
            "after": last_fullname # In PRAW, we use the fullname for the next 'after'
        }

    def _get_best_image(self, submission: Any) -> Optional[str]:
        """
        Attempts to find the best image URL for the submission.
        """
        # 1. Try preview images (often high res)
        if hasattr(submission, 'preview') and 'images' in submission.preview:
            try:
                return submission.preview['images'][0]['source']['url']
            except (IndexError, KeyError):
                pass

        # 2. If it's a direct image link
        url = getattr(submission, 'url', '')
        if url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return url

        # 3. Fallback to thumbnail
        thumbnail = getattr(submission, 'thumbnail', None)
        if thumbnail and thumbnail not in ('default', 'self', 'nsfw', ''):
            return thumbnail

        return None

    async def close(self):
        await self.reddit.close()
