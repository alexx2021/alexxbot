import asyncio
import datetime
import time
from discord.ext.commands.cooldowns import BucketType
from utils.utils import blacklist_user_main, gech_main, help_paginate
import discord
from discord.ext import commands
import os
import logging
import aiosqlite
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




bot = commands.Bot(
command_prefix= get_prefix, 
case_insensitive=True, 
intents=intents, 
allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False), 
activity=discord.Streaming(name=f"_help", url='https://www.twitch.tv/alexxwastakenlol')
)


class MyHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(command_attrs={
        'cooldown': commands.Cooldown(1, 5, commands.BucketType.user), 
        'max_concurrency': commands.MaxConcurrency(1, per=commands.BucketType.user, wait=False)})
    
    bot.linksString = 'ℹ️ [Support Server](https://discord.gg/zPWMRMXQ7H)\n🎉 [Invite Me!](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=2080763127&scope=bot)'
    
    # help
    async def send_bot_help(self, mapping):
        """ Sends the main help menu """
        e = discord.Embed(title=f"Alexx-bot Help", color = discord.Color.blurple(), description=bot.linksString)
        perms = self.context.channel.permissions_for(self.context.guild.me)
        for cog in bot.cogs:
            counter = 0
            for command in bot.get_cog(cog).get_commands():
                if command.hidden:
                    pass
                else:
                    counter += 1
            if counter != 0:
                if perms.add_reactions:
                    cmdHelp = ''
                    e.set_footer(text='React below to view help for each category!')
                else:
                    cmdHelp = f'`{self.clean_prefix}help {cog}`\n'
                cogObj = bot.get_cog(cog)
                e.add_field(name=cog, value=f'{cmdHelp}{cogObj.description}', inline = False)
        helpMessage = await self.context.reply(embed=e)
        await help_paginate(self, bot, helpMessage)
       
   # help <command>
    async def send_command_help(self, command):
        """ Generates a string of how to use a command """
        e = discord.Embed(title=f"Alexx-bot Help", color = discord.Color.blurple())
        temp = f'**Command**\n`{self.clean_prefix}'
        # Aliases
        if len(command.aliases) == 0:
            temp += f'{command.name}'
        elif len(command.aliases) == 1:
            temp += f'[{command.name}|{command.aliases[0]}]'
        else:
            t = '|'.join(command.aliases)
            temp += f'[{command.name}|{t}]'
        # Parameters
        params = command.signature
        temp += f' {params}`\n**Description**\n{command.help}'
        e.description = temp
        e.set_footer(text='<> denotes a required argument | [] denotes an optional argument')
        await self.context.reply(embed = e)
      
   # help <group>
    async def send_group_help(self, group):
        """ Generates help for groups """
        e = discord.Embed(title="Alexx-bot Help", color = discord.Color.blurple())
        temp = f"**{str(group)}**\n{group.short_doc}\n\n"
        for command in group.commands:
            if command.hidden:
                temp += ''
            elif command.help is None:
                temp += f'`{self.clean_prefix}{command}`\n'
            else:
                temp += f'`{self.clean_prefix}{command}` '
                temp += f'{command.help}\n'
        e.description = temp
        e.set_footer(text=f'Use "{self.clean_prefix}help <command>" for info on a specific command')
        await self.context.reply(embed = e)
        
    
   # help <cog>
    async def send_cog_help(self, cog):
        """ Generates help for cogs """
        e = discord.Embed(title="Alexx-bot Help", color = discord.Color.blurple())
        temp = f"**{cog.qualified_name}**\n{cog.description}\n\n"
        for command in cog.get_commands():
            if command.hidden:
                temp += ''
            elif command.help is None:
                temp += f'`{self.clean_prefix}{command}`\n'
            else:
                temp += f'`{self.clean_prefix}{command}` '
                temp += f'{command.help}\n'
        e.description = temp
        e.set_footer(text=f'Use "{self.clean_prefix}help <command>" for info on a specific command')
        await self.context.reply(embed = e)

bot.help_command = MyHelp()

def def_value():
    return False

#cache database stuff
bot.prefixes = {}
bot.ubl = defaultdict(def_value)
bot.whitelist = defaultdict(def_value)
bot.logcache = {}
bot.autorolecache = {}
bot.welcomecache = {}
bot.arelvlsenabled = {}
bot.xpignoredchannels = {}
bot.xproles = {}

#users who spam get added to a dict, and if they spam 5 times they get auto-blacklisted from the bot
bot._auto_spam_count = Counter()

#help command dict LOL
bot.help_menu_counter = Counter()

# keeps track of last sent minigame automsg + also if its enabled
bot.autogames = {}

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
    await bot.bl.execute("CREATE TABLE IF NOT EXISTS whitelist(guild_id INTERGER)")

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
        await bot.sc.execute("CREATE TABLE IF NOT EXISTS autogames(guild_id INTERGER, channel_id INTERGER)")


        await bot.sc.execute("CREATE TABLE IF NOT EXISTS levelrewards(guild_id INTERGER, level INTERGER, role_id INTERGER)")
        await bot.sc.execute("CREATE TABLE IF NOT EXISTS ignoredchannels(guild_id INTERGER, channel_id INTERGER)")
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS chatlvlsenabled(guild_id INTERGER, enabled TEXT)")  #lvls in general       
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS lvlsenabled(guild_id INTERGER, enabled TEXT)") #lvl msgs
        await bot.xp.execute("CREATE TABLE IF NOT EXISTS xp(guild_id INTERGER, user_id INTERGER, user_xp INTERGER)")



async def setup_stuff(bot):
    await blacklist_setup()
    await setup_db(True) # set to false if you do not need tables to be created
    
    guilds = await bot.pr.execute_fetchall("SELECT * FROM prefixes") # prefix cache
    for guild in guilds:
        bot.prefixes[f"{guild[0]}"] = f"{guild[1]}"

    
    users = await bot.bl.execute_fetchall("SELECT * FROM userblacklist") #blacklist cache
    yes = True
    for user in users:
        bot.ubl[user[0]] = yes

    guilds = await bot.bl.execute_fetchall("SELECT * FROM whitelist") #whitelist cache
    yes = True
    for guild in guilds:
        bot.whitelist[guild[0]] = yes
    

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

    autogameguilds = await bot.sc.execute_fetchall("SELECT * FROM autogames") #auto games channel
    for row in autogameguilds:
        tempDict = {
        "lastrun" : time.time(),
        "channel_id" : row[1],
        "ongoing" : 0
        }
        bot.autogames[row[0]] = tempDict

    guilds = await bot.sc.execute_fetchall("SELECT * FROM ignoredchannels") #ingored channels for chat lvl
    for channel in guilds:
        try:    
            bot.xpignoredchannels[channel[0]][channel[1]] = channel[1]
        except KeyError:
            di = {channel[1]: channel[1]}
            bot.xpignoredchannels[channel[0]] = di

    
    print('cache is setup!!')
    print(f'blacklist - {bot.ubl}')


extensions = (
        "admin",
        "autoroles",
        "chatxp",
        "configuration",
        "errors",
        "fun",
        "games",
        "giveaway",
        "invites",
        "logging",
        "misc",
        "moderation",
        "music",
        "reminders",
        "stats",
        "utility",
        "welcome",
        "autogames",
        'cplusplus'
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




spam_control = commands.CooldownMapping.from_cooldown(9, 12, commands.BucketType.user)
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



bot.socketStats = Counter()
@bot.listen()
async def on_socket_response(message):  # this event isn't documented
    msg = message["t"] #is the event name
    #update the counter with this event name
    bot.socketStats[msg] += 1
    #print(msg)

@commands.is_owner()
@bot.command(hidden=True)
async def socket(ctx):
    content = ''
    for item in list(bot.socketStats):
        if not item == None:
            content += f"{item} {bot.socketStats[item]}\n"
    await ctx.send(content)




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
