import pytest_asyncio
import discord
import discord.ext.commands as commands
import discord.ext.test as dpytest


@pytest_asyncio.fixture
async def bot():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    b = commands.Bot(command_prefix="!",
                    intents=intents)
    await b._async_setup_hook()
    dpytest.configure(b)
    return b
