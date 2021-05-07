import asyncio
import discord
import logging
import time
import re

from discord.ext import commands

logger = logging.getLogger('discord')

async def blacklist_setup(bot):
    await bot.db.execute("CREATE TABLE IF NOT EXISTS userblacklist(user_id BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS guildblacklist(guild_id BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS whitelist(guild_id BIGINT)")

async def setup_db(bot):
    await bot.db.execute("CREATE TABLE IF NOT EXISTS prefixes(guild_id BIGINT, prefix TEXT)")

    await bot.db.execute("CREATE TABLE IF NOT EXISTS giveaways(guild_id BIGINT, channel_id BIGINT, message_id BIGINT, user_id BIGINT, future BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS reminders(user_id BIGINT, ctx_id BIGINT, future BIGINT, remindtext TEXT)")

    await bot.db.execute("CREATE TABLE IF NOT EXISTS pmuted_users(guild_id BIGINT, user_id BIGINT)")

    await bot.db.execute("CREATE TABLE IF NOT EXISTS welcome(guild_id BIGINT, log_channel BIGINT, wMsg TEXT, bMsg TEXT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS logging(guild_id BIGINT, log_channel BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS autorole(guild_id BIGINT, role_id BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS autogames(guild_id BIGINT, channel_id BIGINT, delay BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS reactionroles(guild_id BIGINT, message_id BIGINT, reaction TEXT, role_id BIGINT)")


    await bot.db.execute("CREATE TABLE IF NOT EXISTS xp_rewards(guild_id BIGINT, level BIGINT, role_id BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS xp_ignoredchannels(guild_id BIGINT, channel_id BIGINT)")
    await bot.db.execute("CREATE TABLE IF NOT EXISTS xp_enabled(guild_id BIGINT, enabled TEXT)")  #lvls in general       
    await bot.db.execute("CREATE TABLE IF NOT EXISTS xp_lvlup(guild_id BIGINT, enabled TEXT)") #lvl msgs
    await bot.db.execute("CREATE TABLE IF NOT EXISTS xp(guild_id BIGINT, user_id BIGINT, user_xp BIGINT)")
    print('bop')    



async def setup_stuff(bot):
    await blacklist_setup(bot)
    await setup_db(bot)
    async with bot.db.acquire() as connection:
        guilds = await connection.fetch("SELECT * FROM prefixes") # prefix cache
        for guild in guilds:
            prefix = guild["prefix"]
            bot.cache_prefixes[guild["guild_id"]] = f"{prefix}"

        
        users = await connection.fetch("SELECT * FROM userblacklist") #blacklist cache
        yes = True
        for user in users:
            bot.cache_ubl[user["user_id"]] = yes

        servers = await connection.fetch("SELECT * FROM whitelist") #whitelist cache
        yes = True
        for server in servers:
            bot.cache_whitelist[server["guild_id"]] = yes
        

        logs = await connection.fetch("SELECT * FROM logging") #logging ch cache
        for log in logs:
            l_CH = log["log_channel"]
            bot.cache_logs[log["guild_id"]] = f"{l_CH}"

        roles = await connection.fetch("SELECT * FROM autorole") #autorole id cache
        for role in roles:
            r_ID = role["role_id"]
            bot.cache_autorole[role["guild_id"]] = f"{r_ID}"

        msgs = await connection.fetch("SELECT * FROM welcome")
        for msg in msgs:
            di = {
            "logch" : msg["log_channel"], 
            "wMsg" : msg["wmsg"],
            "bMsg" : msg["bmsg"]
                    }
            bot.cache_welcome[msg["guild_id"]] = di
        
        xp = await connection.fetch("SELECT * FROM xp_enabled") #chat lvl enabled
        for enabled_ in xp:
            is_e = enabled_["enabled"]
            bot.cache_lvlsenabled[enabled_["guild_id"]] = f"{is_e}"

        xpmsg = await connection.fetch("SELECT * FROM xp_lvlup") #chat lvl enabled
        for enabled__ in xpmsg:
            is_en = enabled__["enabled"]
            bot.cache_lvlupmsg[enabled__["guild_id"]] = f"{is_en}"


        xpguilds = await connection.fetch("SELECT * FROM xp_ignoredchannels") #ingored channels for chat lvl
        for channel in xpguilds:
            try:    
                bot.cache_xpignoredchannels[channel["guild_id"]][channel["channel_id"]] = channel["channel_id"]
            except KeyError:
                di = {channel["channel_id"]: channel["channel_id"]}
                bot.cache_xpignoredchannels[channel["guild_id"]] = di

        xproleguilds = await connection.fetch("SELECT * FROM xp_rewards") #role rewards
        for xprole in xproleguilds:
            try:    
                bot.cache_xproles[xprole["guild_id"]][xprole["level"]] = xprole["role_id"]
            except KeyError:
                di = {xprole["level"]: xprole["role_id"]}
                bot.cache_xproles[xprole["guild_id"]] = di

        autogameguilds = await connection.fetch("SELECT * FROM autogames") #auto games channel
        for row in autogameguilds:
            tempDict = {
            "lastrun" : time.time(),
            "channel_id" : row["channel_id"],
            "ongoing" : 0,
            "delay" : row["delay"]
            }
            bot.autogames[row["guild_id"]] = tempDict

        reactionroles = await connection.fetch("SELECT * FROM reactionroles")
        for rr in reactionroles:
            try:
                bot.cache_reactionroles[rr["guild_id"]]
            except KeyError:
                bot.cache_reactionroles[rr["guild_id"]] = {rr["message_id"]: {rr["reaction"]: rr["role_id"]} }

            try:
                bot.cache_reactionroles[rr["guild_id"]][rr["message_id"]][rr["reaction"]] = rr["role_id"]
            except KeyError:
                bot.cache_reactionroles[rr["guild_id"]][rr["message_id"]] = {rr["reaction"]: rr["role_id"]}


    print(bot.cache_reactionroles)
    print('cache is setup!!')
    print(f'blacklist - {bot.cache_ubl}')
###################################################################################
async def is_def_emoji(self, ctx, emoji):
    reStr = "('?:\U0001f1e6[\U0001f1e8-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f2\U0001f1f4\U0001f1f6-\U0001f1fa\U0001f1fc\U0001f1fd\U0001f1ff])|(?:\U0001f1e7[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ef\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1fe\U0001f1ff])|(?:\U0001f1e8[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ee\U0001f1f0-\U0001f1f5\U0001f1f7\U0001f1fa-\U0001f1ff])|(?:\U0001f1e9[\U0001f1ea\U0001f1ec\U0001f1ef\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1ff])|(?:\U0001f1ea[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ed\U0001f1f7-\U0001f1fa])|(?:\U0001f1eb[\U0001f1ee-\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1f7])|(?:\U0001f1ec[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ee\U0001f1f1-\U0001f1f3\U0001f1f5-\U0001f1fa\U0001f1fc\U0001f1fe])|(?:\U0001f1ed[\U0001f1f0\U0001f1f2\U0001f1f3\U0001f1f7\U0001f1f9\U0001f1fa])|(?:\U0001f1ee[\U0001f1e8-\U0001f1ea\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9])|(?:\U0001f1ef[\U0001f1ea\U0001f1f2\U0001f1f4\U0001f1f5])|(?:\U0001f1f0[\U0001f1ea\U0001f1ec-\U0001f1ee\U0001f1f2\U0001f1f3\U0001f1f5\U0001f1f7\U0001f1fc\U0001f1fe\U0001f1ff])|(?:\U0001f1f1[\U0001f1e6-\U0001f1e8\U0001f1ee\U0001f1f0\U0001f1f7-\U0001f1fb\U0001f1fe])|(?:\U0001f1f2[\U0001f1e6\U0001f1e8-\U0001f1ed\U0001f1f0-\U0001f1ff])|(?:\U0001f1f3[\U0001f1e6\U0001f1e8\U0001f1ea-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f4\U0001f1f5\U0001f1f7\U0001f1fa\U0001f1ff])|\U0001f1f4\U0001f1f2|(?:\U0001f1f4[\U0001f1f2])|(?:\U0001f1f5[\U0001f1e6\U0001f1ea-\U0001f1ed\U0001f1f0-\U0001f1f3\U0001f1f7-\U0001f1f9\U0001f1fc\U0001f1fe])|\U0001f1f6\U0001f1e6|(?:\U0001f1f6[\U0001f1e6])|(?:\U0001f1f7[\U0001f1ea\U0001f1f4\U0001f1f8\U0001f1fa\U0001f1fc])|(?:\U0001f1f8[\U0001f1e6-\U0001f1ea\U0001f1ec-\U0001f1f4\U0001f1f7-\U0001f1f9\U0001f1fb\U0001f1fd-\U0001f1ff])|(?:\U0001f1f9[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ed\U0001f1ef-\U0001f1f4\U0001f1f7\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1ff])|(?:\U0001f1fa[\U0001f1e6\U0001f1ec\U0001f1f2\U0001f1f8\U0001f1fe\U0001f1ff])|(?:\U0001f1fb[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ee\U0001f1f3\U0001f1fa])|(?:\U0001f1fc[\U0001f1eb\U0001f1f8])|\U0001f1fd\U0001f1f0|(?:\U0001f1fd[\U0001f1f0])|(?:\U0001f1fe[\U0001f1ea\U0001f1f9])|(?:\U0001f1ff[\U0001f1e6\U0001f1f2\U0001f1fc])|(?:\U0001f3f3\ufe0f\u200d\U0001f308)|(?:\U0001f441\u200d\U0001f5e8)|(?:[\U0001f468\U0001f469]\u200d\u2764\ufe0f\u200d(?:\U0001f48b\u200d)?[\U0001f468\U0001f469])|(?:(?:(?:\U0001f468\u200d[\U0001f468\U0001f469])|(?:\U0001f469\u200d\U0001f469))(?:(?:\u200d\U0001f467(?:\u200d[\U0001f467\U0001f466])?)|(?:\u200d\U0001f466\u200d\U0001f466)))|(?:(?:(?:\U0001f468\u200d\U0001f468)|(?:\U0001f469\u200d\U0001f469))\u200d\U0001f466)|[\u2194-\u2199]|[\u23e9-\u23f3]|[\u23f8-\u23fa]|[\u25fb-\u25fe]|[\u2600-\u2604]|[\u2638-\u263a]|[\u2648-\u2653]|[\u2692-\u2694]|[\u26f0-\u26f5]|[\u26f7-\u26fa]|[\u2708-\u270d]|[\u2753-\u2755]|[\u2795-\u2797]|[\u2b05-\u2b07]|[\U0001f191-\U0001f19a]|[\U0001f1e6-\U0001f1ff]|[\U0001f232-\U0001f23a]|[\U0001f300-\U0001f321]|[\U0001f324-\U0001f393]|[\U0001f399-\U0001f39b]|[\U0001f39e-\U0001f3f0]|[\U0001f3f3-\U0001f3f5]|[\U0001f3f7-\U0001f3fa]|[\U0001f400-\U0001f4fd]|[\U0001f4ff-\U0001f53d]|[\U0001f549-\U0001f54e]|[\U0001f550-\U0001f567]|[\U0001f573-\U0001f57a]|[\U0001f58a-\U0001f58d]|[\U0001f5c2-\U0001f5c4]|[\U0001f5d1-\U0001f5d3]|[\U0001f5dc-\U0001f5de]|[\U0001f5fa-\U0001f64f]|[\U0001f680-\U0001f6c5]|[\U0001f6cb-\U0001f6d2]|[\U0001f6e0-\U0001f6e5]|[\U0001f6f3-\U0001f6f6]|[\U0001f910-\U0001f91e]|[\U0001f920-\U0001f927]|[\U0001f933-\U0001f93a]|[\U0001f93c-\U0001f93e]|[\U0001f940-\U0001f945]|[\U0001f947-\U0001f94b]|[\U0001f950-\U0001f95e]|[\U0001f980-\U0001f991]|\u00a9|\u00ae|\u203c|\u2049|\u2122|\u2139|\u21a9|\u21aa|\u231a|\u231b|\u2328|\u23cf|\u24c2|\u25aa|\u25ab|\u25b6|\u25c0|\u260e|\u2611|\u2614|\u2615|\u2618|\u261d|\u2620|\u2622|\u2623|\u2626|\u262a|\u262e|\u262f|\u2660|\u2663|\u2665|\u2666|\u2668|\u267b|\u267f|\u2696|\u2697|\u2699|\u269b|\u269c|\u26a0|\u26a1|\u26aa|\u26ab|\u26b0|\u26b1|\u26bd|\u26be|\u26c4|\u26c5|\u26c8|\u26ce|\u26cf|\u26d1|\u26d3|\u26d4|\u26e9|\u26ea|\u26fd|\u2702|\u2705|\u270f|\u2712|\u2714|\u2716|\u271d|\u2721|\u2728|\u2733|\u2734|\u2744|\u2747|\u274c|\u274e|\u2757|\u2763|\u2764|\u27a1|\u27b0|\u27bf|\u2934|\u2935|\u2b1b|\u2b1c|\u2b50|\u2b55|\u3030|\u303d|\u3297|\u3299|\U0001f004|\U0001f0cf|\U0001f170|\U0001f171|\U0001f17e|\U0001f17f|\U0001f18e|\U0001f201|\U0001f202|\U0001f21a|\U0001f22f|\U0001f250|\U0001f251|\U0001f396|\U0001f397|\U0001f56f|\U0001f570|\U0001f587|\U0001f590|\U0001f595|\U0001f596|\U0001f5a4|\U0001f5a5|\U0001f5a8|\U0001f5b1|\U0001f5b2|\U0001f5bc|\U0001f5e1|\U0001f5e3|\U0001f5e8|\U0001f5ef|\U0001f5f3|\U0001f6e9|\U0001f6eb|\U0001f6ec|\U0001f6f0|\U0001f930|\U0001f9c0|[#|0-9]\u20e3"

    thing = re.findall(reStr, emoji)
    return thing




####################################################################################
async def get_or_fetch_channel(self, channel_id):
    """Only queries API if the channel is not in cache."""
    await self.bot.wait_until_ready()
    ch = self.bot.get_channel(int(channel_id))
    if ch:
        #print('get_channel')
        self.bot.gech['Get'] += 1
        return ch

    try:
        ch = await self.bot.fetch_channel(int(channel_id))
    except discord.HTTPException:
        return None
    else:
        #print('fetch_channel')
        self.bot.gech['Fetch'] += 1
        return ch

async def gech_main(bot, channel_id):
    """Gech func for instances where there is no "self" available"""
    await bot.wait_until_ready()
    ch = bot.get_channel(int(channel_id))
    if ch:
        #print('get_channel')
        bot.gech['Get'] += 1
        return ch

    try:
        ch = await bot.fetch_channel(int(channel_id))
    except discord.HTTPException:
        return None
    else:
        #print('fetch_channel')
        bot.gech['Fetch'] += 1
        return ch

async def get_or_fetch_member(self, guild, member_id): #from r danny :)
    """Only queries API if the member is not in cache."""
    member = guild.get_member(int(member_id))
    if member is not None:
        #print('get_member')
        self.bot.gech['Get'] += 1
        return member

    try:
        member = await guild.fetch_member(int(member_id))
    except discord.HTTPException:
        return None
    else:
        #print('fetch_member')
        self.bot.gech['Fetch'] += 1
        return member

async def get_or_fetch_guild(self, guild_id): #from r danny :)
    """Only queries API if the guild is not in cache."""
    guild = self.bot.get_guild(int(guild_id))
    if guild is not None:
        # print('get_guild')
        self.bot.gech['Get'] += 1
        return guild

    try:
        guild = await self.bot.fetch_guild(int(guild_id))
    except discord.HTTPException:
        return None
    else:
        # print('fetch_guild')
        self.bot.gech['Fetch'] += 1
        return guild
########################LOGGING###########################
async def sendlog(self, guild, content):
    try:   
        ch = self.bot.cache_logs[guild.id]
        channel = await get_or_fetch_channel(self, int(ch)) #discord.utils.get(guild.channels, id=int(ch))
        if channel:
            await channel.send(embed=content)
    except KeyError:
        return
    except discord.errors.Forbidden:
        async with self.bot.db.acquire() as connection:
            await connection.execute("DELETE FROM logging WHERE log_channel = $1", int(ch))
        self.bot.cache_logs.pop(guild.id)
        logger.info(msg=f'Deleted log channel b/c the bot did not have perms to speak - {guild} ({guild.id})')
        return

async def sendlogFile(self, guild, content):
    try:   
        ch = self.bot.cache_logs[guild.id]
        channel = await get_or_fetch_channel(self, int(ch)) #discord.utils.get(guild.channels, id=int(ch))
        if channel:
            perms = channel.permissions_for(channel.guild.me)
            if not perms.attach_files:
                return await channel.send('I am missing permissions to send files!')
            await channel.send(file=content)
    except KeyError:
        return
    except discord.errors.Forbidden:
        async with self.bot.db.acquire() as connection:
            await connection.execute("DELETE FROM logging WHERE log_channel = $1", int(ch))
        self.bot.cache_logs.pop(guild.id)
        logger.info(msg=f'Deleted log channel b/c the bot did not have perms to speak - {guild} ({guild.id})')
        return

async def check_if_log(self, guild):
    try:
        self.bot.cache_logs[guild.id]
        #print('CheckifLog True')
        return True
    except KeyError:
        #print('CheckifLog False')
        return False
########################BLACKLIST###########################
async def blacklist_user(self, user: discord.User):
    async with self.bot.db.acquire() as connection:
        await connection.execute("INSERT INTO userblacklist VALUES($1)", user.id)
    
    self.bot.cache_ubl.update({user.id : True})

async def unblacklist_user(self, user: discord.User):
    async with self.bot.db.acquire() as connection:
        await connection.execute("DELETE FROM userblacklist WHERE user_id = $1", user.id)
    
    self.bot.cache_ubl.update({user.id : False})

async def blacklist_user_main(bot, user: discord.User):
    async with bot.db.acquire() as connection:
        await connection.execute("INSERT INTO userblacklist VALUES($1)", user.id)
    
    bot.cache_ubl.update({user.id : True})
########################HELP###########################
async def help_paginate(self, bot, msg):
    perms = self.context.channel.permissions_for(self.context.guild.me)
    if perms.add_reactions:
        await msg.add_reaction('💬')
        await msg.add_reaction('🛠️')
        await msg.add_reaction('🙂')
        await msg.add_reaction('🎮')
        await msg.add_reaction('🚨')
        await msg.add_reaction('💡')
        try:
            await check_reaction_type(self, bot)
        except asyncio.exceptions.TimeoutError:
            try:
                await asyncio.sleep(0.25)
                await msg.clear_reactions()
                del bot.help_menu_counter[f"{self.context.message.author.id}-1"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-2"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-3"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-4"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-5"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-6"]
            except discord.HTTPException:
                pass
            except KeyError:
                pass

            #TODO - POP ID WITH 1-6

async def check_reaction_type(self, bot):
        reaction, person = await bot.wait_for(
        "reaction_add",
        timeout=20,
        check=lambda reaction, user: user == self.context.author
        and reaction.message.channel == self.context.channel)
        #print(bot.help_menu_counter)
        if str(reaction.emoji) == "💬":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-1"]:  
                bot.help_menu_counter[f"{self.context.message.author.id}-1"] += 1
                
                await self.context.send_help('Levels')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)
        elif str(reaction.emoji) == "🛠️":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-2"]:  
                bot.help_menu_counter[f"{self.context.message.author.id}-2"] += 1
                
                await self.context.send_help('Configuration')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "🙂":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-3"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-3"] += 1
                await self.context.send_help('Fun')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "🎮":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-4"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-4"] += 1

                await self.context.send_help('Games')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)


        elif str(reaction.emoji) == "🚨":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-5"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-5"] += 1

                await self.context.send_help('Moderation')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "💡":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-6"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-6"] += 1

                await self.context.send_help('Utility')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        else:
            pass
########################WHITELIST###########################
async def is_wl(ctx):
    # guildlist = [
    # 741054230370189343,
    # 812951618945286185,
    # 704554442153787453,
    # 783345613860372480,
    # 812520226603794432,
    # 597965043333726220,
    # 796212175693152256,
    # ]
    #iridescent
     #alexx support
      #sniper kingdom
       #burrow's resource pack
        #minty
         #server
          #math pre cal 1
    
    bot = ctx.bot
    
    if bot.cache_whitelist[ctx.guild.id] == True:
        return True
    else:
        await ctx.send('<a:x_:826577785173704754> This guild is not whitelisted to use this command.')
        return False