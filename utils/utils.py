import discord
import logging

logger = logging.getLogger('discord')

async def get_or_fetch_channel(self, channel_id):
    """Only queries API if the channel is not in cache."""
    await self.bot.wait_until_ready()
    ch = self.bot.get_channel(int(channel_id))
    if ch:
        #print('get_channel')
        return ch

    try:
        ch = await self.bot.fetch_channel(int(channel_id))
    except discord.HTTPException:
        return None
    else:
        #print('fetch_channel')
        return ch

async def gech_main(bot, channel_id):
    """Gech func for instances where there is no "self" available"""
    await bot.wait_until_ready()
    ch = bot.get_channel(int(channel_id))
    if ch:
        #print('get_channel')
        return ch

    try:
        ch = await bot.fetch_channel(int(channel_id))
    except discord.HTTPException:
        return None
    else:
        #print('fetch_channel')
        return ch

async def get_or_fetch_member(self, guild, member_id): #from r danny :)
    member = guild.get_member(int(member_id))
    if member is not None:
        #print('get_member')
        return member

    try:
        member = await guild.fetch_member(int(member_id))
    except discord.HTTPException:
        return None
    else:
        #print('fetch_member')
        return member

async def get_or_fetch_guild(self, guild_id): #from r danny :)
    guild = self.bot.get_guild(int(guild_id))
    if guild is not None:
        # print('get_guild')
        return guild

    try:
        guild = await self.bot.fetch_guild(int(guild_id))
    except discord.HTTPException:
        return None
    else:
        # print('fetch_guild')
        return guild
########################LOGGING###########################
async def sendlog(self, guild, content):
    try:   
        ch = self.bot.logcache[f"{guild.id}"]
        channel = await get_or_fetch_channel(self, int(ch)) #discord.utils.get(guild.channels, id=int(ch))
        if channel:
            await channel.send(embed=content)
    except KeyError:
        return
    except discord.errors.Forbidden:
        await self.bot.sc.execute("DELETE FROM logging WHERE log_channel = ?",(ch,))
        await self.bot.sc.commit()
        self.bot.logcache.pop(f"{guild.id}")
        logger.info(msg=f'Deleted log channel b/c the bot did not have perms to speak - {guild} ({guild.id})')
        return

async def sendlogFile(self, guild, content):
    try:   
        ch = self.bot.logcache[f"{guild.id}"]
        channel = await get_or_fetch_channel(self, int(ch)) #discord.utils.get(guild.channels, id=int(ch))
        if channel:
            perms = channel.permissions_for(channel.guild.me)
            if not perms.attach_files:
                return await channel.send('I am missing permissions to send files!')
            await channel.send(file=content)
    except KeyError:
        return
    except discord.errors.Forbidden:
        await self.bot.sc.execute("DELETE FROM logging WHERE log_channel = ?",(ch,))
        await self.bot.sc.commit()
        self.bot.logcache.pop(f"{guild.id}")
        logger.info(msg=f'Deleted log channel b/c the bot did not have perms to speak - {guild} ({guild.id})')
        return

async def check_if_log(self, guild):
    try:
        check = self.bot.logcache[f"{guild.id}"]
        #print('CheckifLog True')
        return True
    except KeyError:
        #print('CheckifLog False')
        return False
########################BLACKLIST###########################
async def blacklist_user(self, user):
    await self.bot.bl.execute("INSERT INTO userblacklist VALUES(?)", (user.id,))
    await self.bot.bl.commit()
    
    self.bot.ubl.update({user.id : True})

async def unblacklist_user(self, user):
    await self.bot.bl.execute("DELETE FROM userblacklist WHERE user_id = ?",(user.id,))
    await self.bot.bl.commit()
    
    self.bot.ubl.update({user.id : False})

async def blacklist_user_main(bot, user):
    await bot.bl.execute("INSERT INTO userblacklist VALUES(?)", (user.id,))
    await bot.bl.commit()
    
    bot.ubl.update({user.id : True})
