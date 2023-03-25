import discord
import os

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

def load_token():
    try:
        with open('./token') as token_file:
            return token_file.read().strip()
    except FileNotFoundError:
        print("Unable to start server, missing `token` file")

token = load_token()

if token:
    print("Starting Server!")
    client.run(token)

print("Goodbye")