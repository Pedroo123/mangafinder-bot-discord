import asyncpraw
import html
from typing import Optional, Dict, Any
from config import Config

class RedditService:
    def __init__(self):
        self._reddit: Optional[asyncpraw.Reddit] = None

    def get_reddit(self) -> asyncpraw.Reddit:
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

        reddit = self.get_reddit()
        subreddit = reddit.subreddit(subreddit_name)

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

    def _get_best_image(self, submission: Any) -> Optional[str]:
        """
        Attempts to find the best image URL for the submission.
        Follows a fallback logic: Preview -> Direct Link -> Thumbnail.
        """
        # 1. Try high-resolution preview
        if hasattr(submission, 'preview') and 'images' in submission.preview:
            try:
                images = submission.preview['images']
                if images:
                    source = images[0].get('source')
                    if source:
                            return html.unescape(source.get('url'))
            except (IndexError, AttributeError):
                pass

        # 2. Direct image link check
        url = getattr(submission, 'url', '')
        if url and any(url.lower().endswith(ext) for ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return url

        # 3. Fallback to thumbnail
        thumbnail = getattr(submission, 'thumbnail', None)
        if thumbnail and thumbnail not in ('default', 'self', 'nsfw', ''):
            return thumbnail

        return None

    async def close(self):
        if self._reddit:
            await self._reddit.close()
            self._reddit = None
