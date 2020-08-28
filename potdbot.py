import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix = '.')
POTD_Answer = 'A'

@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == ('ans=' + POTD_Answer):
        await message.author.send('Congratulations! You solved todays POTD!')
    elif message.content.startswith('ans='):
        await message.author.send('Unfortunately, you got the problem wrong. Try again.')


client.run(os.environ['TOKEN'])
