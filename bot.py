import discord
from discord.ext import commands, tasks
from googleapiclient.discovery import build
from flask import Flask
from threading import Thread

# Create a Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return 'Bot is running!'

# Initialize the bot and the YouTube API
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# YouTube API setup
YOUTUBE_API_KEY = 'YOUR_YOUTUBE_API_KEY'  # Replace with your YouTube API key
CHANNEL_ID = 'YOUR_YOUTUBE_CHANNEL_ID'  # YouTube channel ID
DISCORD_CHANNEL_ID = 123456789012345678  # Discord channel ID where notifications will be sent

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

# Track the latest video
latest_video_id = None

def get_latest_video():
    global latest_video_id
    request = youtube.search().list(
        part='snippet',
        channelId=CHANNEL_ID,
        order='date',
        maxResults=1
    )
    response = request.execute()
    video = response['items'][0]
    video_id = video['id']['videoId']
    video_title = video['snippet']['title']
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    return video_id, video_title, video_url

@tasks.loop(minutes=10)  # Check every 10 minutes
async def check_for_new_video():
    global latest_video_id
    new_video_id, video_title, video_url = get_latest_video()
    if new_video_id != latest_video_id:
        latest_video_id = new_video_id
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
        if channel:
            await channel.send(f'New video posted: {video_title} - {video_url}')

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.idle,
        activity=discord.Activity(type=discord.ActivityType.watching, name="YouTube Channel")
    )
    print(f'Logged in as {bot.user}')
    check_for_new_video.start()  # Start the background task

# Run the Flask app and the bot
def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask).start()

# Directly use your bot token here
bot.run('YOUR_DISCORD_BOT_TOKEN')  # Replace with your actual Discord bot token
