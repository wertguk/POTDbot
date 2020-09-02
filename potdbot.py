import discord
import os
from discord.ext import commands
from collections import defaultdict

POTD_Answer = defaultdict(str)
Points = defaultdict(int)
Finished_POTD = defaultdict(int)
Members = defaultdict(list)
leaders = {}

client = commands.Bot(command_prefix = 'r/')
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
    embed.add_field(name='help', value='Pulls up this help page.', inline = False)
    embed.add_field(name='points', value='Checks how many points you have from POTDs. Aliases include pts', inline = False)
    embed.add_field(name='leaderboard', value='Pulls up the leaderboard for the POTDs. Aliases include lb', inline = False)
    embed.add_field(name='change_problem', value='change_problem {problem ans} {point value} {tries}: Changes points and answer value for the POTD. Can only be used by staff.', inline = False)
    embed.add_field(name='change_points', value='change_points {member id} {point value}: Change points for member id and point value. Can only used by staff', inline = False)
    embed.add_field(name='add_member', value='add_member {member id}:Adds member to the bot by member id. This allows them to be on the leaderboard.', inline = False)
    embed.add_field(name='How to answer POTDs', value='DM POTD Bot with your answer! Lower and upper case letters both work for multiple choice.', inline = False)
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
        Finished_POTD[i] = int(arg2)-1
        await solver.remove_roles(role)
        await solver.remove_roles(role2)

@client.command()
@commands.check(check_staff)
async def add_member(ctx, arg1):
    Members[1].append(int(arg1))
    await ctx.send('Member '+arg1+' was added.')

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
    if isinstance(message.channel, discord.channel.DMChannel):
        str(POTD_Answer[1])
        if message.author == client.user:
            return
        if message.author.id in Members[1]:
            pass
        else:
            Finished_POTD[message.author.id]=Points[0]
        if Finished_POTD[message.author.id] != 0:
            if message.content == POTD_Answer[1] or message.content == POTD_Answer[1].lower():
                server = client.get_guild(748268625491656755)
                role = server.get_role(748370861727416341)
                role2 = server.get_role(748635877571297421)
                channel = client.get_channel(748269407964364890)
                solver = server.get_member(message.author.id)
                is_member = False
            
                Points[message.author.id] = Points[message.author.id] + int(Points[0])
                await message.author.send('Congratulations! You solved todays POTD! You earned '+str(Points[0])+' points!')
                Finished_POTD[message.author.id] = 0
                int(Points[0])

                for i in Members[1]:
                    if i==message.author.id:
                        is_member = True
                if is_member == False:
                    Members[1].append(message.author.id)
                
                await channel.send('Congratulations {} for successfully solving todays POTD!'.format(message.author.mention))
                await solver.add_roles(role)
                await solver.add_roles(role2)
            else:
                server = client.get_guild(748268625491656755)
                role2 = server.get_role(748635877571297421)
                solver = server.get_member(message.author.id)
                is_member = False

                await message.author.send('Unfortunately, you got the problem wrong. You have '+str(Finished_POTD[message.author.id])+' tries left.')
                Finished_POTD[message.author.id] = int(Finished_POTD[message.author.id])-1

                for i in Members[1]:
                    if i==message.author.id:
                        is_member = True
                if is_member == False:
                    Members[1].append(message.author.id)
            
                await solver.add_roles(role2)
        else:
            await message.author.send('You have run out of tries, please wait until the next POTD to submit.')

    await client.process_commands(message)

client.run(os.environ['TOKEN'])
