import asyncpraw
import asyncprawcore
import html
import logging
from typing import List, Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class RedditService:
    def __init__(self):
        self.reddit = asyncpraw.Reddit(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            username=Config.REDDIT_USERNAME,
            password=Config.REDDIT_PASSWORD,
            user_agent=Config.REDDIT_USER_AGENT
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

        try:
            subreddit = self.reddit.subreddit(subreddit_name)

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
        except asyncprawcore.exceptions.PRAWException as e:
            logger.error(f"PRAW error during search: {e}")
            # Re-raise PRAW exceptions so the caller can handle specific ones (like Forbidden, NotFound)
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during search: {e}")
            # Re-raise or handle specifically
            raise Exception(f"Reddit search failed: {str(e)}")

    def _get_best_image(self, submission: Any) -> Optional[str]:
        """
        Attempts to find the best image URL for the submission.
        Handles Reddit galleries, previews, and direct links.
        Ensures HTML unescaping for PRAW URLs.
        """
        # 1. Handle Reddit Galleries
        if getattr(submission, 'is_gallery', False) is True:
            try:
                # Get the first item in the gallery
                gallery_data = getattr(submission, 'gallery_data', {})
                if gallery_data and 'items' in gallery_data:
                    first_item_id = gallery_data['items'][0]['media_id']
                    media_metadata = getattr(submission, 'media_metadata', {})
                    if first_item_id in media_metadata:
                        # PRAW might return multiple resolutions, take the highest or source
                        s = media_metadata[first_item_id].get('s')
                        if s and 'u' in s:
                            return html.unescape(s['u'])
            except (AttributeError, IndexError, KeyError):
                pass

        # 2. Try preview images (often high res)
        if hasattr(submission, 'preview') and 'images' in submission.preview:
            try:
                url = submission.preview['images'][0]['source']['url']
                return html.unescape(url)
            except (IndexError, KeyError):
                pass

        # 3. If it's a direct image link
        url = getattr(submission, 'url', '')
        if url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return url

        # 4. Fallback to thumbnail
        thumbnail = getattr(submission, 'thumbnail', None)
        if thumbnail and thumbnail not in ('default', 'self', 'nsfw', ''):
            return thumbnail

        return None

    async def close(self):
        await self.reddit.close()
