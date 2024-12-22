import discord
from discord.ext import commands
import asyncio
import random

# Create a bot instance with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)

# Sample trivia questions and answers
TRIVIA_QUESTIONS = [
    {"question": "What is the capital of France?", "answers": ["Paris"]},
    {"question": "2 + 2 equals?", "answers": ["4", "four"]},
    {"question": "Who wrote '1984'?", "answers": ["George Orwell"]},
]

# Dictionary to track ongoing trivia sessions by channel ID
trivia_sessions = {}

@bot.event
async def on_ready():
    # Log a message when the bot successfully connects
    print(f"Bot connected as {bot.user}")

@bot.command(name='start_trivia')
async def start_trivia(ctx):
    # Check if trivia is already running in the current channel
    if ctx.channel.id in trivia_sessions:
        await ctx.send("Trivia is already in progress in this channel!")
        return

    # Mark this channel as having an active trivia session
    trivia_sessions[ctx.channel.id] = True
    await ctx.send("Starting Secure Trivia Challenge! Answer quickly!")

    # Dictionary to track scores for participants
    scores = {}
    for question in TRIVIA_QUESTIONS:
        # Send the trivia question to the channel
        await ctx.send(f"Question: {question['question']}")

        # Function to validate messages as potential answers
        def check(m):
            # Ensure the message is in the same channel and from a new participant
            return m.channel == ctx.channel and m.author not in scores

        try:
            # Wait for an answer, with a timeout of 15 seconds
            msg = await bot.wait_for('message', check=check, timeout=15.0)
            if msg.content.lower().strip() in [a.lower() for a in question['answers']]:
                # Increment the participant's score for a correct answer
                scores[msg.author] = scores.get(msg.author, 0) + 1
                await ctx.send(f"Correct answer by {msg.author.mention}!")
            else:
                await ctx.send(f"Wrong answer, {msg.author.mention}!")
        except asyncio.TimeoutError:
            # Handle cases where no answer is provided within the time limit
            await ctx.send("Time's up! No one answered correctly.")

    # End the trivia session for this channel
    trivia_sessions.pop(ctx.channel.id, None)
    if scores:
        # Determine the winner based on scores
        winner = max(scores, key=scores.get)
        await ctx.send(f"Trivia ended! Winner: {winner.mention} with {scores[winner]} points!")
    else:
        # Handle the case where no one scored points
        await ctx.send("Trivia ended! No winners this time.")

@bot.command(name='stop_trivia')
async def stop_trivia(ctx):
    # Stop the trivia session if one is active in this channel
    if ctx.channel.id in trivia_sessions:
        trivia_sessions.pop(ctx.channel.id, None)
        await ctx.send("Trivia has been stopped.")
    else:
        await ctx.send("No trivia is currently running in this channel.")

# Run the bot using the provided token
bot.run("YOUR_DISCORD_BOT_TOKEN")

