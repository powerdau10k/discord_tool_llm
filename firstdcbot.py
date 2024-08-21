from scrapetest import simpletest/simpletest
import os
import dotenv
import discord
from responses import get_answer, get_tool
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# bot setup
intents = discord.Intents(messages=True, guilds=True)
intents.message_content = True
client = discord.Client(intents=intents)


# message func
async def send_message(message, user_message):
    if not user_message:
        print("empty user_message")
        return
    if is_private := user_message[0] == "?":
        user_message = user_message[1:]
        response = get_answer(user_message)
        await message.author.send(response)
        return
    elif is_tool := user_message[0] == "!":
        user_message = user_message[1:]
        response = await get_tool(user_message)
        del response[-2]  # redundant "Response to Human:"
        for item in response:  # /n problem fixed
            await message.channel.send(item)
        return

    else:
        response = get_answer(user_message)
        await message.channel.send(response)


# bot startup
@client.event
async def on_ready():
    print(f"{client.user} is now running")


# message handling
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

    print(f"{username} said: '{user_message}' ({channel})")
    await send_message(message, user_message)


def main():
    client.run(token=TOKEN)


if __name__ == "__main__":
    main()
