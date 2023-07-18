from collections import defaultdict
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from pytz import timezone
import json
import os


USE_SAVED_DATA = os.environ.get("USE_SAVED_DATA", "DISABLED")


# Initialize the bot
intents = discord.Intents.default()
intents.guilds = True
intents.presences = True
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client=client)


# Create a dictionary to store the wins and losses
wins = defaultdict(int)
losses = defaultdict(int)


# Prepopulate with old stats
PREVIOUS_WINS = 0
PREVIOUS_LOSSES = 0
wins["legacy"] = PREVIOUS_WINS
losses["legacy"] = PREVIOUS_LOSSES


eastern = timezone('US/Eastern')


# Common date function to make sure everything is using the same format
def get_date() -> str:
    # If it's before 4am, use yesterday's date
    current_time = datetime.now(eastern)
    if current_time.hour < 4:
        return str((current_time - timedelta(days=1)).date())

    return str(datetime.now(eastern).date())


# Save and load via static json file
def save_data():
    if USE_SAVED_DATA == "DISABLED":
        return

    with open('/app/data/data.json', 'w') as f:
        json.dump({'wins': dict(wins), 'losses': dict(losses)}, f)


def load_data():
    if USE_SAVED_DATA == "DISABLED":
        return

    try:
        with open('/app/data/data.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        pass

    wins.update(data['wins'])
    losses.update(data['losses'])


# Define a command to increment the wins counter
@tree.command(name = "win", description="register a win")
async def win(ctx):
    # Get the current user
    user = ctx.user
        
    date_as_string = get_date()

    # Increment the wins counter
    wins[date_as_string] += 1
    save_data()

    # Send a message to the user
    await ctx.response.send_message(f"Congratulations, {user.name}! You have won a game! Today's record is {wins[date_as_string]} - {losses[date_as_string]}")


# Define a command to increment the losses counter
@tree.command(name = "loss", description="register a loss")
async def loss(ctx: commands.Context):
    # Get the current user
    user = ctx.user
    date_as_string = get_date()

    # Increment the losses counter
    losses[date_as_string] += 1
    save_data()

    # Send a message to the user
    await ctx.response.send_message(f"Sorry, {user.name}! You have lost a game! Today's record is {wins[date_as_string]} - {losses[date_as_string]}")


# Define a command to display the wins and losses
@tree.command(name = "today", description="show today's stats")
async def today(ctx: commands.Context):
    date_as_string = get_date()
    todays_wins = wins[date_as_string]
    todays_losses = losses[date_as_string]

    # Send a message to the user with their wins and losses
    await ctx.response.send_message(f'You have won {todays_wins} games and lost {todays_losses} games today.')


# Define a command to display overall data for all users
@tree.command(name = "overall", description="show overall stats")
async def overall(ctx: commands.Context):
    overall_wins = sum(wins.values())
    overall_losses = sum(losses.values())

    await ctx.response.send_message(f'Overall wins: {overall_wins}\nOverall losses: {overall_losses}')


# Define a command to display data for a specific date
@tree.command(name = "date_stats", description="show stats for a specific date")
async def date_stats(ctx: commands.Context, date: str):
    # Validate input
    try:
        datetime.fromisoformat(date)  # Convert the input date to a datetime.date object
    except ValueError:
        await ctx.response.send_message(f'Invalid date format. Please enter the date in the format YYYY-MM-DD')
        return

    if date not in wins:
        await ctx.response.send_message(f'No data for {date}')
        return

    await ctx.response.send_message(f'On {date}:\nWins: {wins[date]}\nLosses: {losses[date]}')


@tree.command(name = "reduce_losses", description="reduce losses by one")
async def reduce_losses(ctx: commands.Context):
    # Get the current date
    date_as_string = get_date()

    # If the user has any losses for the current day
    if losses[date_as_string] > 0:
        # Reduce the user's losses by 1
        losses[date_as_string] -= 1

        # Send a message to the user
        await ctx.response.send_message(f'Your loss has been reduced by 1.')
    # If the user has no losses for the current day
    else:
        # Send a message to the user
        await ctx.response.send_message(f'You have no losses to reduce.')


@tree.command(name = "reduce_wins", description="reduce wins by one")
async def reduce_wins(ctx: commands.Context):
    # Get the current date
    date_as_string = get_date()

    # If the user has any wins for the current day
    if wins[date_as_string] > 0:
        # Reduce the user's wins by 1
        wins[date_as_string] -= 1
        # Send a message to the user
        await ctx.response.send_message(f'Your wins has been reduced by 1.')

    # If the user has no wins for the current day
    else:
        # Send a message to the user
        await ctx.response.send_message(f'You have no wins to reduce.')


@tree.command(name = "best_day", description="reduce wins by one")
async def best_and_worst(ctx: commands.Context):
    best_day = None
    best_win_percent = 0
    
    worst_day = None
    worst_win_percent = 100

    for day, win_count in wins.items():
        loss_count = losses.get(day, 0)
        if (win_count + loss_count) < 5:
            continue

        win_percent = win_count / (win_count + loss_count)
        if win_percent > best_win_percent:
            best_day = day
            best_win_percent = win_percent
        
        if win_percent < worst_win_percent:
            worst_day = day
            worst_win_percent = win_percent

    await ctx.response.send_message(f'Best day was {best_day} at {wins[best_day]} - {losses[best_day]}\n Worst day was {worst_day} at {wins[worst_day]} - {losses[worst_day]}.\n(only counts day with <5 games played)')


# Function to enable validation of win/loss counts during testing
def get_values():
    return wins, losses

def reset_wins_losses():
    global wins, losses
    wins = defaultdict(int)
    losses = defaultdict(int)


@client.event
async def on_ready():
    load_data()
    await tree.sync()


# Run the bot, enter discord bot code below
# client.run('')
