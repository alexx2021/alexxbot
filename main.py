import asyncio
import discord
from discord.ext import commands
import os
import logging
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

    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('_')
    else:
        custom = await bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(msg.guild.id,),)
        if custom !=[]:
            #print(custom[0][1])
            base.append(custom[0][1])
        else:
            base.append('_')

    return base

bot = commands.Bot(command_prefix= get_prefix, case_insensitive=True, help_command=None, intents=intents)
loop = asyncio.get_event_loop()
bot.bl =  loop.run_until_complete(aiosqlite.connect('blacklists.db'))
bot.pr =  loop.run_until_complete(aiosqlite.connect('prefix.db'))


#creates databases if they havent been made yet before loading the cogs
conn = sqlite3.connect('prefix.db')
c = conn.cursor()
conn2 = sqlite3.connect('prefix.db')
c2 = conn.cursor()

def blacklist_setup():
    c2.execute("CREATE TABLE IF NOT EXISTS userblacklist(user_id INTERGER)")
    c2.execute("CREATE TABLE IF NOT EXISTS guildblacklist(guild_id INTERGER)")
    c2.close()
    conn2.close()

def prefix_setup():
    c.execute("CREATE TABLE IF NOT EXISTS prefixes(guild_id INTERGER, prefix TEXT)")
    c.close()
    conn.close()


blacklist_setup()
prefix_setup()



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
    await bot.change_presence(activity=Activity(name=f"alexx.lol | help", type=ActivityType.playing))
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
    p = tuple(await get_prefix(bot,message))

    if message.content.startswith(p): # only query database if a command is run #idk if this is neeeded anymore
        rows = await bot.bl.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(message.author.id,),)
        if rows != []:
            return 

    await bot.process_commands(message)

@bot.command(aliases=["commands", "invite"])
async def help(ctx):
    embed = discord.Embed(color=0)
    embed.title = "Commands help"
    embed.description = ('[alexx.lol (bot wiki)](https://alexx.lol)')
    embed.add_field(name="Other links", value='[Invite link (recommended permissions)](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=8&scope=bot)' 
    + '\n[Invite link (required permissions)](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=2080763127&scope=bot)'
    + '\n[Support Server](https://discord.gg/zPWMRMXQ7H)')
    embed.add_field(name="Prefix", value='You can find my prefix by doing `@alexx prefix` and change it with\n`@alexx setprefix <newprefix>`')
    embed.add_field(name="About", value='A multi-purpose discord bot written in python by `Alexx#7687` that is straightforward and easy to use. \nOh, and how could I forget? Cats. Lots of cats. 🐱')
    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
    
    await ctx.send(embed=embed)


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

@bot.command()
async def prefix(ctx):
    custom = await bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(ctx.guild.id,),)
    if custom:
        await ctx.send(f'The custom prefix for this guild is `{custom[0][1]}`\n You can change it with `{custom[0][1]}setprefix <newprefix>`')
    else:
        await ctx.send(f'The prefix for this guild is `_`\n You can change it with `_setprefix <newprefix>`')

@bot.command(aliases=["changeprefix"])
async def setprefix(ctx, prefix: str):
    if len(prefix) > 20:
        return await ctx.send('Prefix is too long.')
    
    custom = await bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(ctx.guild.id,),)
    if custom:
        await bot.pr.execute("UPDATE prefixes SET prefix = ? WHERE guild_id = ?",(prefix, ctx.guild.id,),)
        await bot.pr.commit()
    else:    
        await bot.pr.execute("INSERT INTO prefixes VALUES (?, ?)",(ctx.guild.id, prefix),)
        await bot.pr.commit()
    await ctx.send(f'Set prefix to `{prefix}`')

@bot.command()
async def dumppr(ctx):
    custom = await bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(ctx.guild.id,),)
    await ctx.send(f'{custom}')



TOKEN = os.getenv("DISCORD_TOKEN2")
bot.run(TOKEN)
