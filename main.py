import asyncio
from discord.ext.commands.cooldowns import CooldownMapping
from utils.utils import blacklist_user_main, gech_main, help_paginate, setup_stuff
import discord
from discord.ext import commands
import os
import logging
import asyncpg
from dotenv import load_dotenv
from collections import Counter, defaultdict

load_dotenv()

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

intents = discord.Intents.all()
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
            if bot.cache_prefixes[msg.guild.id]:
                base.append(str(bot.cache_prefixes[msg.guild.id]))
                #print('used cache for prefix')
                return base
        except KeyError:
            pass
        
        async with bot.db.acquire() as connection:
            custom = await connection.fetchrow("SELECT * FROM prefixes WHERE guild_id = $1", msg.guild.id)
            #print('used db for prefix')
            if custom:
                cust_p = custom["prefix"]
                base.append(custom["prefix"])
                bot.cache_prefixes.update({msg.guild.id : f"{cust_p}"})
            else:
                base.append('_')
                bot.cache_prefixes.update({msg.guild.id : f"_"})

    return base




bot = commands.Bot(
command_prefix= get_prefix, 
case_insensitive=True, 
intents=intents, 
allowed_mentions=discord.AllowedMentions(roles=False, users=True, everyone=False), 
activity=discord.Streaming(name=f"_help", url='https://www.twitch.tv/alexxwastakenlol')
)
bot.launch_time = discord.utils.utcnow()



class MyHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(command_attrs=
        {
        'cooldown': CooldownMapping.from_cooldown(1, 2, commands.BucketType.user), 
        'max_concurrency': commands.MaxConcurrency(2, per=commands.BucketType.user, wait=False)
        }
            )
    
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
            
            if str(cog).lower() == 'jishaku': #dont show jishaku in help menu
                counter = 0

            if counter != 0:
                cmdHelp = f'`{self.context.clean_prefix}help {cog}`\n'
                cogObj = bot.get_cog(cog)
                e.add_field(name=f'{cog[0].upper()}{cog[1:]}', value=f'{cmdHelp}{cogObj.description}', inline = False)
        await self.context.reply(embed=e)
       
   # help <command>
    async def send_command_help(self, command):
        """ Generates a string of how to use a command """
        e = discord.Embed(title=f"Alexx-bot Help", color = discord.Color.blurple())
        temp = f'**Command**\n`{self.context.clean_prefix}'
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
        if str(group).lower() == 'jsk' or str(group).lower() == 'jishaku':
            return #stops overflow

        e = discord.Embed(title="Alexx-bot Help", color = discord.Color.blurple())
        temp = f"**{str(group)}**\n{group.short_doc}\n\n"
        for command in group.commands:
            if command.hidden:
                temp += ''
            elif command.help is None:
                temp += f'`{self.context.clean_prefix}{command}`\n'
            else:
                temp += f'`{self.context.clean_prefix}{command}` '
                temp += f'{command.help}\n'
        e.description = temp
        e.set_footer(text=f'Use "{self.context.clean_prefix}help <command>" for info on a specific command')
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
                temp += f'`{self.context.clean_prefix}{command}`\n'
            else:
                temp += f'`{self.context.clean_prefix}{command}` '
                temp += f'{command.help}\n'
        e.description = temp
        e.set_footer(text=f'Use "{self.context.clean_prefix}help <command>" for info on a specific command')
        await self.context.reply(embed = e)

bot.help_command = MyHelp()

def def_value():
    return False

#cache database stuff
bot.cache_prefixes = {}
bot.cache_ubl = defaultdict(def_value)
bot.cache_whitelist = defaultdict(def_value)
bot.cache_logs = {}
bot.cache_autorole = {}
bot.cache_welcome = {}
bot.cache_lvlsenabled = {}
bot.cache_lvlupmsg = {}
bot.cache_xpignoredchannels = {}
bot.cache_xproles = {}
bot.cache_reactionroles = {}
bot.cache_mediaonly = {}


#users who spam get added to a dict, and if they spam 5 times they get auto-blacklisted from the bot
bot._auto_spam_count = Counter()


#reaction role anti spam dict LOL
bot.reaction_spam = {}

# keeps track of last sent minigame automsg + also if its enabled
bot.autogames = {}


# :eyes:
bot.sp = {}
bot.sp.update({"enabled": False})

#track fetches/gets for the session
bot.gech = Counter()


credentials = {
    "user": "alexander",
    "database": "alexander",
    "host": "127.0.0.1",
}

W_DBPASS = os.getenv("W_DB_PASS")
W_USER = os.getenv("W_DB_USER")
W_DB = os.getenv("W_DB")
credentialsW = {
    "user": W_USER,
    "database": W_DB,
    "host": "127.0.0.1",
    "password": W_DBPASS,
}

DBPASS = os.getenv("DB_PASS")
credentialsVPS = {
    "user": "alexx",
    "database": "alexx",
    "host": "127.0.0.1",
    "password": DBPASS,
}



#global database connections
loop = asyncio.get_event_loop()

bot.db = loop.run_until_complete(asyncpg.create_pool(**credentialsW))



extensions = (
        "admin",
        "autoroles",
        "chatxp",
        "configuration",
        "errors",
        "fun",
        "games",
        "giveaway",
        "logging",
        "misc",
        "moderation",
        "music",
        "reminders",
        "stats",
        "utility",
        "welcome",
        "autogames",
        'cplusplus',
        "reactionroles",
        "mediaonly"
    )

loop.create_task(setup_stuff(bot)) #sets up stuff before cogs load

count = 0
for ext in extensions:
    bot.load_extension(f"cogs.{ext}")
    print(f'Loaded {ext}')
    count += 1

bot.load_extension("jishaku")

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    print('--------------------------')
    print(f'Logged in as: {bot.user.name}')
    print(f'With ID: {bot.user.id}')
    print(f'{count} total extensions loaded')
    print(f"Servers - {str(len(bot.guilds))}")
    print('--------------------------')
    print('Bot is ready!')


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
    embed.timestamp = discord.utils.utcnow()
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
            if retry_after and ctx.message.author.id != 982849405357019166: # last number is 6
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
    if message.author.bot:
        return
        
    p = tuple(await get_prefix(bot, message))

    if message.content.startswith(p): # only query cache if a command is run
        if bot.cache_ubl[message.author.id] == True:
            return

######################################################################################################

    if not message.author.bot: #bots dont trigger this
        if message.content in [f'<@!{bot.user.id}>', f'<@{bot.user.id}>']: #check if msg is a mention
            
            if bot.cache_ubl[message.author.id] == True:
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
    async with bot.db.acquire() as connection:
        guilds = await connection.fetch("SELECT * FROM prefixes")
    print('-----------dump-----------')
    print(guilds)
    print('--------------------------')
    print(bot.cache_prefixes)
    print('-----------dump-----------')

@commands.is_owner()
@bot.command(hidden=True)
async def dumpbl(ctx):
    async with bot.db.acquire() as connection:
        users = await connection.fetch("SELECT * FROM userblacklist")
    print('-----------dump-----------')
    print(users)
    print('--------------------------')
    print(bot.cache_ubl)
    print('-----------dump-----------')



TOKEN = os.getenv("DISCORD_TOKEN2")
bot.run(TOKEN)