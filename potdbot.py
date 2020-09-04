import discord
import asyncpg
import os
from discord.ext import commands
from collections import defaultdict

POTD_Answer = defaultdict(str)
Points = defaultdict(int)
leaders = {}

client = commands.Bot(command_prefix = '$')
client.remove_command('help')

async def create_db_pool():
    client.pg_con = await asyncpg.create_pool(database='potd_db', user='postgres', password=os.environ['pg_password'])

def check_staff(ctx):
    if ctx.message.author.id == 358334606975434752:
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
    embed.add_field(name='add_member', value='add_member {member id}:Adds member by member id. This allows them to be on the leaderboard.', inline = False)
    embed.add_field(name='remove_member', value='remove_member {member id}:Removes member by member id.', inline = False)
    embed.add_field(name='How to answer POTDs', value='DM POTD Bot with your answer! Lower and upper case letters both work for multiple choice.', inline = False)
    await ctx.send(embed=embed)

@client.command(aliases = ['lb'])
async def leaderboard(ctx):
    x = await client.pg_con.fetch('SELECT COUNT(user_id) FROM users')
    y = str(x[0])
    y = list(y)
    num_users = []
    for i in range(len(y)):
        if y[i].isnumeric() == True:
            num_users.append(y[i])
            
    num_users = int(''.join(num_users))

    for i in range(num_users):
        user = await client.pg_con.fetchrow('SELECT * FROM users LIMIT 1 OFFSET $1', i)
        print(user)
        member = user['user_id']
        pts = user['points']
        leaders.update({member: pts})
        
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

    x = await client.pg_con.fetch('SELECT COUNT(user_id) FROM users')
    y = str(x[0])
    y = list(y)
    num_users = []
    for i in range(len(y)):
        if y[i].isnumeric() == True:
            num_users.append(y[i])

    num_users = int(''.join(num_users))
    members = []
    for i in range(num_users):
        user = await client.pg_con.fetchrow('SELECT * FROM users LIMIT 1 OFFSET $1', i)
        members.append(user['user_id'])
    print(members)

    for i in members:
        await client.pg_con.execute('UPDATE users SET tries = $1 WHERE user_id = $2', int(arg2), i)
        member = i
        
        solver = server.get_member(member)
        await solver.remove_roles(role)
        await solver.remove_roles(role2)

@client.command()
@commands.check(check_staff)
async def add_member(ctx, arg1):
    user = await client.pg_con.fetch('SELECT * FROM users WHERE user_id = $1', int(arg1))

    if not user:
        await client.pg_con.execute('INSERT INTO users(user_id, points, tries) VALUES ($1, 0, $2)', int(arg1), Points[0])
        await ctx.send('Member '+arg1+' was added.')
    else:
        await ctx.send(arg1+' is already a member.')

@client.command()
@commands.check(check_staff)
async def remove_member(ctx, arg1):
    user = await client.pg_con.fetch('SELECT * FROM users WHERE user_id = $1', int(arg1))

    if user:
        await client.pg_con.execute('DELETE FROM users WHERE user_id = $1', int(arg1))
        await ctx.send('Member '+arg1+' was removed.')
    else:
        await ctx.send(arg1+' is not a member.')

@client.command()
@commands.check(check_staff)
async def change_points(ctx, arg1, arg2):
    pts = await client.pg_con.fetch('SELECT points FROM users WHERE user_id = $1', int(arg1))
    pts = int(arg2)
    await client.pg_con.execute('UPDATE users SET points = $1 WHERE user_id = $2', int(arg2), int(arg1))
    await ctx.send('Member '+arg1+' points has been changed to '+arg2)

@client.command(aliases = ['pts'])
async def points(ctx):
    pts = await client.pg_con.fetch('SELECT points FROM users WHERE user_id = $1', ctx.message.author.id)
    await ctx.send('You have '+str(pts)+' points.')

@client.event
async def on_message(message):
    if isinstance(message.channel, discord.channel.DMChannel):
        if message.author == client.user:
            return

        user = await client.pg_con.fetch('SELECT * FROM users WHERE user_id = $1', message.author.id)

        if not user:
            await client.pg_con.execute('INSERT INTO users(user_id, points, tries) VALUES ($1, 0, $2)', message.author.id, int(Points[0]))

        user = await client.pg_con.fetchrow('SELECT * FROM users WHERE user_id = $1', message.author.id)

        attempts = user['tries']
        
        #if you have tries left
        if attempts != 0:
            #if you answered correctly
            if message.content == POTD_Answer[1] or message.content == POTD_Answer[1].lower():
                server = client.get_guild(748268625491656755)
                role = server.get_role(748370861727416341)
                role2 = server.get_role(748635877571297421)
                channel = client.get_channel(748269407964364890)
                solver = server.get_member(message.author.id)

                pts = user['points']
                pts = pts + int(attempts)

                await client.pg_con.execute('UPDATE users SET points = $1 WHERE user_id = $2', int(pts), message.author.id)
                await client.pg_con.execute('UPDATE users SET tries = 0 WHERE user_id = $1', message.author.id)
                await message.author.send('Congratulations! You solved todays POTD! You earned '+str(attempts)+' points!')
                await channel.send('Congratulations {} for successfully solving todays POTD!'.format(message.author.mention))
                await solver.add_roles(role)
                await solver.add_roles(role2)
            #if you answered incorrectly
            else:
                server = client.get_guild(748268625491656755)
                role2 = server.get_role(748635877571297421)
                solver = server.get_member(message.author.id)

                attempts = attempts-1
                await message.author.send('Unfortunately, you got the problem wrong. You have '+str(attempts)+' tries left.')

                await client.pg_con.execute('UPDATE users SET tries = $1 WHERE user_id = $2', attempts, message.author.id)

                if attempts == 0:
                    await solver.add_roles(role2)
        else:
            await message.author.send('You dont have any tries left, please wait until the next POTD to submit.')

    await client.process_commands(message)

client.loop.run_until_complete(create_db_pool())
client.run(os.environ['TOKEN'])
