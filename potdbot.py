import discord
import os
from discord.ext import commands
from collections import defaultdict

POTD_Answer = defaultdict(str)
Points = defaultdict(int)
Finished_POTD = defaultdict(int)
Members = defaultdict(list)
leaders = {}

client = commands.Bot(command_prefix = '$')
client.remove_command('help')

def check_staff(ctx):
    if ctx.message.author.id == 358334606975434752 or ctx.message.author.id == 329054903937007617:
        return True
    else:
        return False

@client.event
async def on_ready():
    print('Bot is ready.')

@client.command()
async def help(ctx):
    embed = discord.Embed(title = 'POTD Bot Help', description = 'List of commands for POTD Bot', colour = discord.Colour.blue())
    embed.add_field(name='!help', value='Pulls up this help page.')
    embed.add_field(name='!points', value='Checks how many points you have from POTDs. Aliases include !pts', inline = False)
    embed.add_field(name='!leaderboard', value='Pulls up the leaderboard for the POTDs. Aliases include !lb')
    embed.add_field(name='!change_problem', value='Changes points and answer value for the POTD. Can only be used by Heran.', inline = False)
    embed.add_field(name='How to answer POTDs', value='Instructions are pinned in the announcements page.', inline = False)
    await ctx.send(embed=embed)

@client.command(aliases = ['lb'])
async def leaderboard(ctx):
    for i in range(len(Members[1])):
        leaders.update({Members[1][i]: Points[Members[1][i]]})
    sorted_leaders = sorted(leaders.items(), key=lambda kv: kv[1], reverse=True)
    embed = discord.Embed(title = 'Leaderboard', description = 'List of scores for POTDs', colour = discord.Colour.orange())
    x=1
    for j in sorted_leaders:
        user = client.get_user(j[0])
        embed.add_field(name=str(x)+'. '+str(user), value=str(j[1]), inline = False)
        x=x+1
    await ctx.send(embed=embed)

@client.command()
@commands.check(check_staff)
async def change_problem(ctx, arg1, arg2):
    server = client.get_guild(748268625491656755)
    role = server.get_role(748370861727416341)
    role2 = server.get_role(748635877571297421)
    
    POTD_Answer[1] = arg1
    Points[0] = arg2
    await ctx.send('OK, changed POTD answer to ' + arg1 +' and changed point value to '+arg2)
    for i in Members[1]:
        solver = server.get_member(i)
        Finished_POTD[i] = 0
        await solver.remove_roles(role)
        await solver.remove_roles(role2)

@client.command()
@commands.check(check_staff)
async def change_points(ctx, arg1, arg2):
    Points[int(arg1)] = int(arg2)
    await ctx.send('Member '+arg1+' points has been changed to '+arg2)

@client.command(aliases = ['pts'])
async def points(ctx):
    await ctx.send('You have '+str(Points[ctx.message.author.id])+' points.')

@client.event
async def on_message(message):
    str(POTD_Answer[1])
    if message.author == client.user:
        return
    if Finished_POTD[message.author.id] != 1:
        if message.content == ('ans=' + POTD_Answer[1]):
            server = client.get_guild(748268625491656755)
            role = server.get_role(748370861727416341)
            role2 = server.get_role(748635877571297421)
            channel = client.get_channel(748269407964364890)
            solver = server.get_member(message.author.id)
            is_member = False
            
            Points[message.author.id] = Points[message.author.id] + int(Points[0])
            await message.author.send('Congratulations! You solved todays POTD! You earned '+str(Points[0])+' points!')
            Finished_POTD[message.author.id] = 1
            int(Points[0])

            for i in Members[1]:
                if i==message.author.id:
                    is_member = True
            if is_member == False:
                Members[1].append(message.author.id)
            
            await channel.send('Congratulations {} for successfully solving todays POTD!'.format(message.author.mention))
            await solver.add_roles(role)
            await solver.add_roles(role2)
        elif message.content.startswith('ans='):
            server = client.get_guild(748268625491656755)
            role2 = server.get_role(748635877571297421)
            solver = server.get_member(message.author.id)
            is_member = False

            await message.author.send('Unfortunately, you got the problem wrong. You dont get any points today. :(')
            Finished_POTD[message.author.id] = 1

            for i in Members[1]:
                if i==message.author.id:
                    is_member = True
            if is_member == False:
                Members[1].append(message.author.id)
            
            await solver.add_roles(role2)
    else:
        if message.content.startswith('ans='):
            await message.author.send('You have already answered todays POTD. Please wait for the next POTD to submit.')
    await client.process_commands(message)

client.run(os.environ['TOKEN'])
