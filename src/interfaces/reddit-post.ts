interface RedditPost {
    id: string,
    title: string,
    url?: string,
    permalink?: string,
    author?: string,
    created_utc?: string,
    score?: string,
    num_comments?: number,
    subreddit?: string
}