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
    await bot.db.execute("CREATE TABLE IF NOT EXISTS mediaonly(guild_id BIGINT, channel_id BIGINT)")


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


        mediaonly = await connection.fetch("SELECT * FROM mediaonly") 
        for channel in mediaonly:
            try:    
                bot.cache_mediaonly[channel["guild_id"]][channel["channel_id"]] = channel["channel_id"]
            except KeyError:
                di = {channel["channel_id"]: channel["channel_id"]}
                bot.cache_mediaonly[channel["guild_id"]] = di


    print('cache is setup!!')
    print(f'blacklist - {bot.cache_ubl}')




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

async def check_if_important_msg(self, guildID, messageID):
    try:
        self.bot.cache_reactionroles[guildID].pop(messageID)
        
        async with self.bot.db.acquire() as connection:
            await connection.execute('DELETE FROM reactionroles WHERE guild_id = $1 AND message_id = $2', guildID, messageID)
    except KeyError:
        return
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
        await msg.add_reaction('⏰')
        await msg.add_reaction('💡')
        try:
            await check_reaction_type(self, bot)
        except asyncio.exceptions.TimeoutError:
            try:
                del bot.help_menu_counter[f"{self.context.message.author.id}-1"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-2"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-3"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-4"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-5"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-6"]
                del bot.help_menu_counter[f"{self.context.message.author.id}-7"]
            except KeyError:
                pass
            
            
            try:
                await asyncio.sleep(0.25)
                await msg.clear_reactions()
            except discord.HTTPException:
                await msg.remove_reaction('💬', bot.user)
                await msg.remove_reaction('🛠️', bot.user)
                await msg.remove_reaction('🙂', bot.user)
                await msg.remove_reaction('🎮', bot.user)
                await msg.remove_reaction('🚨', bot.user)
                await msg.remove_reaction('⏰', bot.user)
                await msg.remove_reaction('💡', bot.user)
        


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
                
                await self.context.send_help('levels')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)
        elif str(reaction.emoji) == "🛠️":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-2"]:  
                bot.help_menu_counter[f"{self.context.message.author.id}-2"] += 1
                
                await self.context.send_help('configuration')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "🙂":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-3"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-3"] += 1
                await self.context.send_help('fun')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "🎮":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-4"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-4"] += 1

                await self.context.send_help('games')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)


        elif str(reaction.emoji) == "🚨":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-5"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-5"] += 1

                await self.context.send_help('moderation')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "💡":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-6"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-6"] += 1

                await self.context.send_help('utility')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        elif str(reaction.emoji) == "⏰":
            if not bot.help_menu_counter[f"{self.context.message.author.id}-7"]:
                bot.help_menu_counter[f"{self.context.message.author.id}-7"] += 1

                await self.context.send_help('reminders')
                await check_reaction_type(self,bot)
            else:
                await check_reaction_type(self,bot)

        else:
            pass
########################WHITELIST###########################
async def is_wl(ctx):
    bot = ctx.bot
    
    if (bot.cache_whitelist[ctx.guild.id] == True) or (ctx.author.id == 247932598599417866):
        return True
    else:
        await ctx.send('<a:x_:826577785173704754> This guild is not whitelisted to use this command.')
        return False
############################LEVELING##################################
async def addRoles(self, message, level):
    if message.guild.me.guild_permissions.manage_roles:
        try:    
            r = self.bot.cache_xproles[message.guild.id][level]
        except KeyError:
            return
        role = discord.utils.get(message.guild.roles, id= int(r))
        if role:
            if message.guild.me.top_role.position > role.position:
                await message.author.add_roles(role, reason=f"Role reward for level {level}.")

async def on_level_up(self, level: int, message: discord.Message):
    try:
        if 'TRUE' in self.bot.cache_lvlupmsg[message.guild.id]:
            await addRoles(self, message, level)
        else:
            return await addRoles(self, message, level)
    except KeyError:
        return await addRoles(self, message, level)
    
    perms = message.channel.permissions_for(message.guild.me)
    if perms.send_messages: #only send if we can
        await message.channel.send(
            f"Nice job {message.author.mention}, you are now level **{level}**!")

############################TIME CONVERTER##################################
async def convertTime(self, ctx, argument):
    time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
    time_dict = {"h":3600, "s":1, "m":60, "d":86400}
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for v, k in matches:
        try:
            time += time_dict[k]*float(v)
        except KeyError:
            raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
        except ValueError:
            raise commands.BadArgument("{} is not a number!".format(v))
    return time