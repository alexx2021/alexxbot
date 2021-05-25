import logging
import discord
import asyncio
from discord.ext import commands
logger = logging.getLogger('discord')


class mediaOnly(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            try:
                self.bot.cache_mediaonly[message.guild.id][message.channel.id]
            except KeyError:
                return
            if not message.attachments:
                if not message.author.bot:
                    if not ((message.author.guild_permissions.manage_guild) or (message.author.guild_permissions.administrator)):

                        #perms = message.channel.permissions_for(message.guild.me)

                        if message.guild.me.guild_permissions.manage_messages:

                            try:
                                await message.delete()
                            except discord.errors.NotFound:
                                pass
                            except discord.errors.Forbidden:
                                try:    
                                    self.bot.cache_mediaonly[message.guild.id].pop(message.channel.id)
                                    async with self.bot.db.acquire() as connection:
                                        await connection.execute('DELETE FROM mediaonly WHERE guild_id = $1 AND channel_id = $2', message.guild.id, message.channel.id)
                                except KeyError:
                                    logger.info(msg=f'Deleted mediaonly cfg b/c the bot did not have perms to delete - {message.guild} ({message.guild.id})')
                                    
                            #await asyncio.sleep(0.25)
                            #await message.channel.send(f'{message.author.mention}, this is a __media only__ channel!', delete_after = 4)



def setup(bot):
	bot.add_cog(mediaOnly(bot))