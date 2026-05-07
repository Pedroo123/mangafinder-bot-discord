import asyncpraw
import asyncprawcore
import html
import logging
from typing import List, Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class RedditService:
    """
    Service class to interact with the Reddit API using asyncpraw.
    """
    def __init__(self):
        """
        Initializes the Reddit service with credentials from the configuration.
        """
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
        """
        Searches for posts in a specific subreddit.

        Args:
            subreddit_name: The name of the subreddit to search in.
            query: The search query.
            limit: The maximum number of results to return.
            sort: How to sort the results (e.g., 'new', 'relevance').
            after: The fullname of a post to start the search after (for pagination).

        Returns:
            A dictionary containing a list of posts and the 'after' fullname.
        """
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

            logger.info(f"Found {len(posts)} posts for query '{query}' in r/{subreddit_name}")
            return {
                "posts": posts,
                "after": last_fullname
            }
        except asyncprawcore.exceptions.PRAWException as e:
            logger.error(f"PRAW error during search: {e}")
            raise Exception(f"Reddit API error: {str(e)}")
        except Exception as e:
            logger.exception(f"Unexpected error during search: {e}")
            raise Exception(f"Reddit search failed: {str(e)}")

    def _get_best_image(self, submission: Any) -> Optional[str]:
        """
        Attempts to find the best image URL for the submission.
        Handles HTML unescaping for PRAW URLs.

        Args:
            submission: The asyncpraw Submission object.

        Returns:
            A string containing the best image URL found, or None.
        """
        # 1. Try preview images (often high res)
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
            return thumbnail

        return None

    async def close(self):
        """
        Closes the underlying asyncpraw Reddit instance.
        """
        await self.reddit.close()
