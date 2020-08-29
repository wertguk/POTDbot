import discord
import os
from discord.ext import commands
from collections import defaultdict

POTD_Answer = defaultdict(str)
client = commands.Bot(command_prefix = '!')

def check_if_it_is_me(ctx):
    return ctx.message.author.id == 358334606975434752

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
@commands.check(check_if_it_is_me)
async def change_ans(ctx, arg):
    POTD_Answer[1] = arg
    await ctx.send('OK, changed POTD answer to ' + arg)

@client.event
async def on_message(message):
    str(POTD_Answer[1])
    if message.author == client.user:
        return
    if message.content == ('ans=' + POTD_Answer[1]):
        await message.author.send('Congratulations! You solved todays POTD!')
    elif message.content.startswith('ans='):
        await message.author.send('Unfortunately, you got the problem wrong. Try again.')
    await client.process_commands(message)


client.run(os.environ['TOKEN'])
