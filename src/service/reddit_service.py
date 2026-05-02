import asyncpraw
import html
from typing import Optional, Dict, Any
from config import Config

class RedditService:
    def __init__(self):
        # We don't initialize reddit here to avoid using Config before it might be validated
        # or if we want to defer it.
        self._reddit = None

    @property
    def reddit(self):
        if self._reddit is None:
            self._reddit = asyncpraw.Reddit(
                client_id=Config.REDDIT_CLIENT_ID,
                client_secret=Config.REDDIT_CLIENT_SECRET,
                username=Config.REDDIT_USERNAME,
                password=Config.REDDIT_PASSWORD,
                user_agent=Config.REDDIT_USER_AGENT
            )
        return self._reddit

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

        # In asyncpraw, reddit.subreddit(name) is a synchronous call that returns a Subreddit object.
        subreddit = self.reddit.subreddit(subreddit_name)

        try:
            # search() returns an AsyncListingGenerator
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
                "after": last_fullname
            }
        except Exception as e:
            raise Exception(f"Reddit API error: {str(e)}")

    def _get_best_image(self, submission: Any) -> Optional[str]:
        """
        Attempts to find the best image URL for the submission.
        """
        # 1. Try preview images (high res)
        if hasattr(submission, 'preview') and 'images' in submission.preview:
            try:
                url = submission.preview['images'][0]['source']['url']
                return html.unescape(url)
            except (IndexError, KeyError):
                pass

        # 2. If it's a direct image link
        url = getattr(submission, 'url', '')
        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return url

        # 3. Fallback to thumbnail
        thumbnail = getattr(submission, 'thumbnail', None)
        if thumbnail and thumbnail not in ('default', 'self', 'nsfw', ''):
            if thumbnail.startswith('http'):
                return html.unescape(thumbnail)

        return None

    async def close(self):
        if self._reddit:
            await self._reddit.close()
