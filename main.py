import asyncio
import datetime
from utils.utils import blacklist_user_main, gech_main
import discord
from discord.ext import commands
import os
import logging
import aiosqlite
import aiohttp
from dotenv import load_dotenv
from collections import Counter, defaultdict
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

async def make_session(bot):
    bot.session = aiohttp.ClientSession(loop=bot.loop)
    print('Global session created.')



bot = commands.Bot(
command_prefix= get_prefix, 
case_insensitive=True, 
intents=intents, 
allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False), 
activity=Activity(name=f"alexx.lol | _help", type=ActivityType.playing)
)

bot.remove_command('help')

def def_value():
    return False

#cache database stuff
bot.prefixes = {}
bot.ubl = defaultdict(def_value)
bot.logcache = {}
bot.autorolecache = {}
bot.welcomecache = {}
bot.arelvlsenabled = {}

#users who spam get added to a dict, and if they spam 5 times they get auto-blacklisted from the bot
bot._auto_spam_count = Counter()

#global database connections
loop = asyncio.get_event_loop()
bot.bl = loop.run_until_complete(aiosqlite.connect('blacklists.db'))
bot.pr = loop.run_until_complete(aiosqlite.connect('prefix.db'))
bot.sc = loop.run_until_complete(aiosqlite.connect('serverconfigs.db'))
bot.rm = loop.run_until_complete(aiosqlite.connect('reminders.db'))
bot.m = loop.run_until_complete(aiosqlite.connect('muted.db')) #todo - maybe merge this with another db?
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

        await bot.sc.execute("CREATE TABLE IF NOT EXISTS logging(server_id INTERGER, log_channel INTERGER, whURL TEXT)")
        await bot.sc.execute("CREATE TABLE IF NOT EXISTS autorole(guild_id INTERGER, role_id INTERGER)")

        await bot.xp.execute("CREATE TABLE IF NOT EXISTS chatlvlsenabled(guild_id INTERGER, enabled TEXT)")  #lvls in general       
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS lvlsenabled(guild_id INTERGER, enabled TEXT)") #lvl msgs
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS xp(guild_id INTERGER, user_id INTERGER, user_xp INTERGER)")



async def setup_stuff(bot):
    await make_session(bot)
    await blacklist_setup()
    await setup_db(True) # set to false if you do not need tables to be created
    
    guilds = await bot.pr.execute_fetchall("SELECT * FROM prefixes") # prefix cache
    for guild in guilds:
        bot.prefixes[f"{guild[0]}"] = f"{guild[1]}"

    
    users = await bot.bl.execute_fetchall("SELECT * FROM userblacklist") #blacklist cache
    yes = True
    for user in users:
        bot.ubl[user[0]] = yes
    

    logs = await bot.sc.execute_fetchall("SELECT server_id, log_channel FROM logging") #logging ch cache
    for log in logs:
        bot.logcache[f"{log[0]}"] = f"{log[1]}"

    roles = await bot.sc.execute_fetchall("SELECT * FROM autorole") #autorole id cache
    for role in roles:
        bot.autorolecache[f"{role[0]}"] = f"{role[1]}"

    msgs = await bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome")
    for msg in msgs:
        di = {
        "logch" : msg[1], 
        "wMsg" : msg[2],
        "bMsg" : msg[3]
                }
        bot.welcomecache[f'{msg[0]}'] = di
    
    xp = await bot.xp.execute_fetchall("SELECT * FROM chatlvlsenabled") #chat lvl enabled
    for enabled in xp:
        bot.arelvlsenabled[f"{enabled[0]}"] = f"{enabled[1]}"

    
    print('cache is setup!!')
    print(f'blacklist - {bot.ubl}')


extensions = (
        "admin",
        "autoroles",
        "chatxp",
        "configuration",
        "customhelp",
        "errors",
        "fun",
        "games",
        "giveaway",
        "invites",
        "logging",
        "misc",
        "moderation",
        "music",
        "nsfw",
        "reminders",
        "stats",
        "utility",
        "welcome",
    )

loop.create_task(setup_stuff(bot)) #sets up stuff before cogs load

count = 0
for ext in extensions:
    bot.load_extension(f"cogs.{ext}")
    print(f'Loaded {ext}')
    count += 1

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print('--------------------------')
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    print(f'{count} total extensions loaded')
    print(f"Servers - {str(len(bot.guilds))}")
    print('--------------------------')

    # the rest  of the startup output is in Invites.py

async def log_spammer(ctx, message, retry_after, *, autoblock=False):
    ch = await gech_main(bot, 813600852576829470)

    guild_name = getattr(ctx.guild, 'name', 'No Guild (DMs)')
    guild_id = getattr(ctx.guild, 'id', None)
    fmt =f'User {message.author} (ID {message.author.id}) in guild {guild_name} (ID {guild_id}) spamming, retry_after: {round(retry_after, 2)}'
    logger.warning(msg=fmt)
    print(fmt)
    if not autoblock:
        return
    
    embed = discord.Embed(title='Auto-blocked Member', colour=discord.Color.red())
    embed.add_field(name='Member', value=f'{message.author} (ID: {message.author.id})', inline=False)
    embed.add_field(name='Guild Info', value=f'{guild_name} (ID: {guild_id})', inline=False)
    embed.add_field(name='Channel Info', value=f'{message.channel} (ID: {message.channel.id}', inline=False)
    embed.timestamp = datetime.datetime.utcnow()
    return await ch.send(embed=embed)




spam_control = commands.CooldownMapping.from_cooldown(10, 12, commands.BucketType.user)
#reduces forbiddden errors due to not being able to respond to commands lol
#the autoblacklist stuff is also mashed up in here cause you apparantly (cant spell) cant have more than one bot.check
@bot.check_once
async def can_do_stuff(ctx: commands.Context):
    if ctx.message.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            return False
        elif not perms.embed_links:
            await ctx.send('I require permission to send embeds in order to work.')
            return False
        else:
            bucket = spam_control.get_bucket(ctx.message)
            retry_after = bucket.update_rate_limit()
            if retry_after and ctx.message.author.id != 247932598599417866: # last number is 6
                bot._auto_spam_count[ctx.message.author.id] += 1
                if bot._auto_spam_count[ctx.message.author.id] >= 5:
                    del bot._auto_spam_count[ctx.message.author.id]
                    await log_spammer(ctx, ctx.message, retry_after, autoblock=True)
                    await blacklist_user_main(bot, ctx.author)
                else:
                    await log_spammer(ctx, ctx.message, retry_after)
                return False
            else:
                if bot._auto_spam_count[ctx.message.author.id] <= 3:
                    bot._auto_spam_count.pop(ctx.message.author.id, None)
                return True         

@bot.command(hidden=True)
async def bop(ctx):
    pass

@bot.event
async def on_message(message: discord.Message):
    await bot.wait_until_ready()

    if not message.guild:
        return
        
    p = tuple(await get_prefix(bot, message))

    if message.content.startswith(p): # only query cache if a command is run
        if bot.ubl[message.author.id] == True:
            return

######################################################################################################

    if not message.author.bot: #bots dont trigger this
        if message.content in [f'<@!{bot.user.id}>', f'<@{bot.user.id}>']: #check if msg is a mention
            
            if bot.ubl[message.author.id] == True:
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
                        e = discord.Embed(color=0, description= f'The prefix for this guild is `{p[2]}`\n You can change it with `{p[2]}setprefix <newprefix>`', title=':eyes: - Hello there!')
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
