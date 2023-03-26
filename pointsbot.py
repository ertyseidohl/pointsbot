"""Python discord bot for granting and tracking points."""

import os
import traceback

import discord

from pointsdb import PointsDB # pylint: disable=import-error
from pointsprocessor import PointsProcessor, CommandException # pylint: disable=import-error

CURRENCY_SYMBOL = "ꙮ"

def attach_events(client, processor):
    """Attach events to Discord client."""

    @client.event
    async def on_ready():
        print(f"We have logged in as {client.user}")

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if processor.is_command(message):
            try:
                response = processor.process(message)
            except CommandException as exception:
                traceback.print_exc()
                response = "Oops: " + str(exception)
            except Exception as exception: # pylint: disable=broad-exception-caught
                traceback.print_exc()
                response = "ERROR: " + str(exception)

            await message.channel.send(response,
                allowed_mentions=discord.AllowedMentions.none())

def load_token():
    """Load the token from a local private file called `token`"""
    try:
        with open(os.path.dirname(__file__) + "/token", encoding="UTF-8") as token_file:
            return token_file.read().strip()
    except FileNotFoundError:
        print("Unable to start server, missing `token` file")
        raise

def init():
    """Initalize server."""
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    client = discord.Client(intents=intents)
    token = load_token()
    points_db = PointsDB()
    points_processor = PointsProcessor(points_db=points_db, currency_symbol=CURRENCY_SYMBOL)

    if token:
        print("Starting Server!")
        attach_events(client, points_processor)
        client.run(token)

init()
print("Goodbye!")
