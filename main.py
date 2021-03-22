import asyncio
import discord
from discord.embeds import Embed
from discord.ext import commands
import os
import logging
from discord.ext.commands.core import has_permissions
import psutil
import datetime
import aiosqlite
import sqlite3
from dotenv import load_dotenv
from discord import Activity, ActivityType

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.typing = False
intents.presences = False



async def get_prefix(bot, msg):

    # user_id = bot.user.id
    # base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    base = []
    if msg.guild is None:
        base.append('_')
    else:
        try:   
            if bot.prefixes[f"{msg.guild.id}"]:
                base.append(str(bot.prefixes[f"{msg.guild.id}"]))
                #print('used cache for prefix')
                return base
        except KeyError:
            pass
        
        custom = await bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(msg.guild.id,),)
        #print('used db for prefix')
        if custom != []:
            base.append(custom[0][1])
            bot.prefixes.update({f"{msg.guild.id}" : f"{custom[0][1]}"})
        else:
            base.append('_')
            bot.prefixes.update({f"{msg.guild.id}" : f"_"})

    return base

class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=0, description='[Click me for a detailed command list](http://alexx.lol)\n[Support Server](https://discord.gg/zPWMRMXQ7H)\n',title='Alexx-bot Help')
        for page in self.paginator.pages:
            e.description += page
        e.add_field(name='Invite me!', value='[Invite link (recommended)](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=8&scope=bot)' 
    + '\n[Invite link (required)](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=2080763127&scope=bot)')
        await destination.send(embed=e)


bot = commands.Bot(command_prefix= get_prefix, case_insensitive=True, intents=intents, help_command = MyHelpCommand())
bot.prefixes = {}
bot.ubl = {}
bot.logcache = {}

loop = asyncio.get_event_loop()
bot.bl = loop.run_until_complete(aiosqlite.connect('blacklists.db'))
bot.pr = loop.run_until_complete(aiosqlite.connect('prefix.db'))
bot.sc = loop.run_until_complete(aiosqlite.connect('serverconfigs.db'))
bot.rm = loop.run_until_complete(aiosqlite.connect('reminders.db'))
bot.m = loop.run_until_complete(aiosqlite.connect('muted.db'))
bot.i = loop.run_until_complete(aiosqlite.connect('invites.db'))



async def blacklist_setup():
    await bot.bl.execute("CREATE TABLE IF NOT EXISTS userblacklist(user_id INTERGER)")
    await bot.bl.execute("CREATE TABLE IF NOT EXISTS guildblacklist(guild_id INTERGER)")

async def setup_db(choice):
    if choice == True:
        print('bop')    
        await bot.pr.execute("CREATE TABLE IF NOT EXISTS prefixes(guild_id INTERGER, prefix TEXT)")

        await bot.rm.execute("CREATE TABLE IF NOT EXISTS giveaways(guild_id INTERGER, channel_id INTERGER, message_id INTERGER, user_id INTERGER, future INTERGER)")
        await bot.rm.execute("CREATE TABLE IF NOT EXISTS reminders(id INTERGER, future INTERGER, remindtext TEXT)")

        await bot.m.execute("CREATE TABLE IF NOT EXISTS pmuted_users(guild_id INTERGER, user_id INTERGER)")

        await bot.sc.execute("CREATE TABLE IF NOT EXISTS welcome(server_id INTERGER, log_channel INTERGER, wMsg TEXT, bMsg TEXT)")
        #bot.sc.execute("CREATE TABLE IF NOT EXISTS welcomeinvite(server_id INTERGER, log_channel INTERGER, whURL TEXT)") #not sure if I want to keep this, might merge with welcome
        await bot.sc.execute("CREATE TABLE IF NOT EXISTS logging(server_id INTERGER, log_channel INTERGER, whURL TEXT)")
        
        await bot.i.execute("CREATE TABLE IF NOT EXISTS invites(guild_id INTERGER, user_id INTERGER, inv_count INTERGER, inv_by INTERGER)")


async def setup_stuff():
    await blacklist_setup()
    await setup_db(True) # set to false if you do not need tables to be created
    
    guilds = await bot.pr.execute_fetchall("SELECT * FROM prefixes") # prefix cache
    for guild in guilds:
        bot.prefixes[f"{guild[0]}"] = f"{guild[1]}"

    
    users = await bot.bl.execute_fetchall("SELECT * FROM userblacklist") #blacklist cache
    totalusers = []
    for user in users:
        totalusers.append(str(user[0]))
    bot.ubl[f"users"] = f"{totalusers}"
    

    logs = await bot.sc.execute_fetchall("SELECT server_id, log_channel FROM logging") #logging ch cache
    for log in logs:
        bot.logcache[f"{log[0]}"] = f"{log[1]}"
    
    print('cache is setup!!')
    # print(f'prefixes - {bot.prefixes}')
    #print(f'logs - {bot.logcache}')
    print(f'blacklist - {bot.ubl}')


loop.create_task(setup_stuff()) #sets up stuff before cogs load

try: #tries to load cogs in the correct path for the bot host
    for filename in os.listdir('/home/container/cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename[:-3]}')
except: #if it fails, looks in a different path (for my own testing purposes)
    for filename in os.listdir('/users/alexander/documents/repo#2/alexxbot/cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename[:-3]}')




@bot.event
async def on_ready():
    await bot.wait_until_ready()
    await bot.change_presence(activity=Activity(name=f"alexx.lol | _help", type=ActivityType.playing))
    print('--------------------------')
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    print('--------------------------')

    # the rest  of the startup output is in Invites.py



# ############################user blacklist
# @bot.check_once
# async def is_blacklisted(ctx):
#     print('checked')
#     async with aiosqlite.connect('blacklists.db') as c:
#         rows = await c.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(ctx.author.id,),)
#         if rows != []:
#             return False
#         else:
#             return True


@bot.event
async def on_message(message: discord.Message):
    await bot.wait_until_ready()

    if not message.guild:
        return
        
    p = tuple(await get_prefix(bot, message))

    if message.content.startswith(p): # only query database if a command is run
#################
        if str(message.author.id) in bot.ubl["users"]:
            return
        
        # rows = await bot.bl.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(message.author.id,),)
        # print('used db for bl')
        # if rows != []:
        #     everyone = list(bot.ubl["users"])
        #     everyone.append(message.author.id)
        #     bot.ubl.update({f"users" : f"{everyone}"})
        #     return
#################
    if not message.author.bot:
        if message.content in [f'<@!{bot.user.id}>', f'<@{bot.user.id}>']:
            if str(message.author.id) in bot.ubl["users"]:
                return
            
            # rows = await bot.bl.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(message.author.id,),)
            # print('used db for bl')
            # if rows != []:
            #     everyone = list(bot.ubl["users"])
            #     everyone.append(message.author.id)
            #     bot.ubl.update({f"users" : f"{everyone}"})
            #     return
            e = discord.Embed(color=0, description= f'The prefix for this guild is `{p[0]}`\n You can change it with `{p[0]}setprefix <newprefix>`')
            await message.channel.send(embed=e)

    await bot.process_commands(message)



#about command
@commands.cooldown(2, 6, commands.BucketType.user)
@bot.command(aliases=["info", "about"],help="Gives you information about the bot and its owner, as well as an invite like for the bot.")
async def botinfo(ctx):
    embed = discord.Embed(color=0x7289da)
    embed.title = "About the Bot"
    embed.description = ('A multi-purpose discord bot written in python by `Alexx#7687` that is straightforward and easy to use. \nOh, and how could I forget? Cats. Lots of cats. 🐱')
    embed.add_field(name='Useful links', 
    value=('[Invite link (recommended)](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=8&scope=bot)' 
    + '\n[Invite link (required)](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=2080763127&scope=bot)'
    + '\n[Support Server](https://discord.gg/zPWMRMXQ7H)'
    + '\n[Commands help](http://alexx.lol)'), inline = True)
    embed.add_field(name='Total servers', value=f' {len(bot.guilds)}', inline = True)
    embed.add_field(name='Total users', value = f'{len(set(bot.get_all_members()))}', inline = True)
    embed.add_field(name='Ping', value=f'{round(bot.latency * 1000)}ms', inline = True)
    embed.add_field(name='RAM Usage', value=f'{psutil.virtual_memory()[2]}%', inline = True)
    embed.add_field(name='CPU Usage', value=f'{psutil.cpu_percent()}%', inline = True)
    embed.timestamp = datetime.datetime.utcnow()
    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

@has_permissions(manage_guild=True)
@commands.cooldown(2, 10, commands.BucketType.guild)
@bot.command(aliases=["changeprefix", "prefix"])
async def setprefix(ctx, prefix: str):
    await bot.wait_until_ready()
    if len(prefix) > 20:
        return await ctx.send('Prefix is too long.')
    
    custom = await bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(ctx.guild.id,),)
    if custom:
        await bot.pr.execute("UPDATE prefixes SET prefix = ? WHERE guild_id = ?",(prefix, ctx.guild.id,),)
        await bot.pr.commit()
        bot.prefixes.update({f"{ctx.guild.id}" : f"{prefix}"})
    else:    
        await bot.pr.execute("INSERT INTO prefixes VALUES (?, ?)",(ctx.guild.id, prefix),)
        await bot.pr.commit()
        bot.prefixes.update({f"{ctx.guild.id}" : f"{prefix}"})
    await ctx.send(f'Set prefix to `{prefix}`')

@commands.is_owner()
@bot.command(hidden=True)
async def dumppr(ctx):
    guilds = await bot.pr.execute_fetchall("SELECT * FROM prefixes")
    print('-----------dump-----------')
    print(guilds)
    print('--------------------------')
    print(bot.prefixes)
    print('-----------dump-----------')

@commands.is_owner()
@bot.command(hidden=True)
async def dumpbl(ctx):
    users = await bot.bl.execute_fetchall("SELECT * FROM userblacklist")
    print('-----------dump-----------')
    print(users)
    print('--------------------------')
    print(bot.ubl)
    print('-----------dump-----------')



TOKEN = os.getenv("DISCORD_TOKEN2")
bot.run(TOKEN)
