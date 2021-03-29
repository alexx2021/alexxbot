import asyncio
import discord
from discord.ext import commands
import os
import logging
import aiosqlite
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



async def get_prefix(bot, msg: discord.Message):

    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    # base = []
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



bot = commands.Bot(command_prefix= get_prefix, case_insensitive=True, intents=intents)
bot.remove_command('help')
bot.prefixes = {}
bot.ubl = {}
bot.logcache = {}
bot.autorolecache = {}

loop = asyncio.get_event_loop()
bot.bl = loop.run_until_complete(aiosqlite.connect('blacklists.db'))
bot.pr = loop.run_until_complete(aiosqlite.connect('prefix.db'))
bot.sc = loop.run_until_complete(aiosqlite.connect('serverconfigs.db'))
bot.rm = loop.run_until_complete(aiosqlite.connect('reminders.db'))
bot.m = loop.run_until_complete(aiosqlite.connect('muted.db'))
bot.xp = loop.run_until_complete(aiosqlite.connect('chatxp.db'))



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
        await bot.sc.execute("CREATE TABLE IF NOT EXISTS autorole(guild_id INTERGER, role_id INTERGER)")
        
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS lvlsenabled(guild_id INTERGER, enabled TEXT)")
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS xp(guild_id INTERGER, user_id INTERGER, user_xp INTERGER)")



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

    roles = await bot.sc.execute_fetchall("SELECT * FROM autorole") #autorole id cache
    for role in roles:
        bot.autorolecache[f"{role[0]}"] = f"{role[1]}"
    
    print('cache is setup!!')
    # print(f'prefixes - {bot.prefixes}')
    #print(f'logs - {bot.logcache}')
    #print(f'aRole - {bot.autorolecache}')
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

#reduces forbiddden errors due to not being able to respond to commands lol
@bot.check_once
async def can_do_stuff(ctx: commands.Context):
    if ctx.message.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            return False
        elif not perms.embed_links:
            await ctx.send('I am missing permissions to send embeds :(')
            return False
        else:
            return True



@bot.event
async def on_message(message: discord.Message):
    await bot.wait_until_ready()

    if not message.guild:
        return
        
    p = tuple(await get_prefix(bot, message))

    if message.content.startswith(p): # only query cache if a command is run
        if str(message.author.id) in bot.ubl["users"]:
            return

######################################################################################################

    if not message.author.bot: #bots dont trigger this
        if message.content in [f'<@!{bot.user.id}>', f'<@{bot.user.id}>']: #check if msg is a mention
            
            if str(message.author.id) in bot.ubl["users"]: #blacklist check
                return
            else:
                if message.guild:
                    perms = message.channel.permissions_for(message.guild.me) #get perms for channel the bot will respond in
                    if not perms.send_messages:
                        return #dont do anything if the bot cannot speak in that channel
                    elif not perms.embed_links:
                        await message.channel.send('I am missing permissions to send embeds :(')
                        return #let the server know if the bot cannot send embeds
                    else:
                        e = discord.Embed(color=0, description= f'The prefix for this guild is `{p[2]}`\n You can change it with `{p[2]}setprefix <newprefix>`')
                        await message.channel.send(embed=e) #send embed if all is good

    await bot.process_commands(message)




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
