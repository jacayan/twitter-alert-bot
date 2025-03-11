import discord
import tweepy
import asyncio

from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Convert to integer
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")

# Set up Discord client
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Set up Tweepy client
twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN)

# Track last seen tweet for each account
last_tweet_id = None

async def check_tweets():
    global last_tweet_id
    await client.wait_until_ready()
    channel = client.get_channel(CHANNEL_ID)

    while True:
        try:
            # Fetch latest tweets from the account
            user = twitter_client.get_user(username=TWITTER_USERNAME)
            print("Fetched user details")
            tweets = twitter_client.get_users_tweets(
                id=user.data.id,
                max_results=5
            )
            print("Fetched tweets from account")
            if tweets.data:
                for tweet in tweets.data:
                    if last_tweet_id is None or tweet.id > last_tweet_id:
                        # Send the tweet to Discord
                        await channel.send(f"New tweet from {TWITTER_USERNAME}: https://twitter.com/{TWITTER_USERNAME}/status/{tweet.id}")
                        print("Tweet sent to Discord channel")
                        last_tweet_id = tweet.id

        except tweepy.errors.TooManyRequests as e:
            print("Rate limit exceeded. Sleeping for 15 minutes...")
            await asyncio.sleep(15 * 60)  # Wait for 15 minutes if rate limit is exceeded
        
        except Exception as e:
            print(f"Error: {e}")

        # Wait 60 seconds before checking again
        await asyncio.sleep(60)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

async def main():
    # Start the scraping task
    client_task = asyncio.create_task(check_tweets())
    await client.start(DISCORD_TOKEN)  # Start the bot

# Use asyncio.run to initialize the bot
if __name__ == "__main__":
    asyncio.run(main())