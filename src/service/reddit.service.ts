import Snoowrap from "snoowrap";
import * as dotenv from "dotenv";

dotenv.config();

export class RedditService {
    constructor() {}

    public async searchSubReddit(subRedditName: string, query: string) {

        const apiRequest = new Snoowrap({
            userAgent: 'MangaFinderBot/1.0 by YourUsername',
            clientId: process.env.REDDIT_CLIENT_ID || '',
            clientSecret: process.env.REDDIT_CLIENT_SECRET || '',
            username: process.env.REDDIT_USERNAME || '',
            password: process.env.REDDIT_PASSWORD || '',
        });

        try {
            const results = 
                await apiRequest.getSubreddit(subRedditName).search({
                    query: query,
                    sort: 'relevance',
                    time: 'week'
            });
            
            results.forEach(post => console.log(post.title));

            return {
                success: true,
                data: results
            }
        } catch (error) {
            throw error;
        }
    }
}