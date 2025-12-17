import axios, { AxiosInstance } from "axios";
import * as dotenv from "dotenv";
dotenv.config();

export class RedditService {
    private axiosInstance: AxiosInstance;
    private token?: {
        acces_token: string,
        expires_at: number
    };
    private readonly USER_AGENT = process.env.REDDIT_USER_AGENT || "mangafinder-bot/0.1 by Brankksss";
    
    constructor() {
        this.axiosInstance = axios.create({
            baseURL: 'https://oauth.reddit.com',
            timeout: 10000,
            headers: {
                "User-Agent": this.USER_AGENT
            }
        });
    }

    private async getAccessToken(): Promise<string> {
        const now = Date.now();

        if (this.token && this.token.expires_at > now) return this.token.acces_token;

        const clinetId = process.env.REDDIT_CLIENT_ID;
        const clientSecret = process.env.REDDIT_CLIENT_SECRET;
        const username = process.env.REDDIT_USERNAME;
        const password = process.env.REDDIT_PASSWORD;

        if (!clinetId || !clientSecret || !username || !password) {
            throw new Error("Missing Reddit credentials");
        };

        const auth = Buffer.from(`${clinetId}:${clientSecret}`).toString("base64");
        const body = new URLSearchParams({
            grant_type: "password",
            username,
            password
        }).toString();

        let lastErr: undefined;
        for (let tentativa = 0; tentativa < 3; tentativa++) {
            try {
                const res = await axios.post("https://www.reddit.com/api/v1/access_token", body, {
                    headers: {
                        Authorization: `Basic ${auth}`,
                        "User-Agent": this.USER_AGENT,
                        "Content-Type": "application/x-www-form-urlencoded"
                    },
                    timeout: 8000,
                });

                const data = res.data;

                if (!data || !data.acces_token || !data.expires_in)
                    throw new Error("Invalid token response");

                const expires_at = Date.now() + (data.expires_in - 60) * 1000;
                this.token = { acces_token: data.acces_token, expires_at };

                return data.acces_token;
            } catch (err: any) {
                lastErr = err;

                const wait = 300 * Math.pow(2, tentativa);
                await new Promise((r) => setTimeout(r, wait));
            }
        }
        throw lastErr;
    }

    public async searchSubReddit(
        subRedditName: string, 
        query: string,
        limit = 25,
        sort: "new" | "hot" | "top" | "relevance" = "new",
        after?: string
    ): Promise<{posts: RedditPost[]; after?: string}> {
        if (!subRedditName) throw new Error("subReddit Name is required");
        if (!query) throw new Error("query is required");

        const token = await this.getAccessToken();
        this.axiosInstance.defaults.headers.common.Authorization = `Bearer ${token}`;

        try {
            const res = await this.axiosInstance.get(`/r/${encodeURIComponent(subRedditName)}/search`, 
            {
                params: { q: query, limit, restrict_sr: true, sort, after },
            });
            
            if (res.status === 429) {
                const retryAfter = Number(res.headers["retry-after"] || 1);
                await new Promise((r) => setTimeout(r, Math.max(1000, retryAfter * 1000)));
            }

            const children = res.data?.data?.children ?? [];
            const posts: RedditPost[] = children.map((c: any) => {
                const d = c.data ?? {};
                return {
                    id: d.id,
                    title: d.title,
                    url: d.url,
                    permalink: d.permalink ? `https://reddit.com${d.permalink}` : undefined,
                    author: d.author,
                    created_utc: d.created_utc,
                    score: d.score,
                    num_comments: d.num_comments,
                    subreddit: d.subreddit,
                };
            });

            return { posts, after: res.data?.data?.after };
        } catch (err: any) {
            const msg = err?.response?.data || err?.message || err;
            throw new Error(`Reddit search failed: ${JSON.stringify(msg)}`);
        } 
    }
}