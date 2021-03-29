import discord
import logging

logger = logging.getLogger('discord')

async def get_or_fetch_channel(self, guild, channel_id):
    await self.bot.wait_until_ready()
    ch = guild.get_channel(int(channel_id))
    if ch:
        #print('get_channel')
        return ch

    try:
        ch = await self.bot.fetch_channel(channel_id)
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
        member = await guild.fetch_member(member_id)
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
        guild = await self.bot.fetch_guild(guild_id)
    except discord.HTTPException:
        return None
    else:
        # print('fetch_guild')
        return guild
########################LOGGING###########################
async def sendlog(self, guild, content):
    try:   
        ch = self.bot.logcache[f"{guild.id}"]
        channel = discord.utils.get(guild.channels, id=ch)
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

async def check_if_log(self, guild):
    try:
        check = self.bot.logcache[f"{guild.id}"]
        #print('CheckifLog True')
        return True
    except KeyError:
        #print('CheckifLog False')
        return False