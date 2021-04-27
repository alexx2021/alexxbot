from utils.utils import get_or_fetch_channel
import discord
import logging
from discord.ext import commands
logger = logging.getLogger('discord')

class Welcome(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot    



    @commands.Cog.listener()
    async def on_member_join(self, member):
        #await asyncio.sleep(1)
        server = member.guild.id
        
        
        try:   
            data = self.bot.cache_welcome[member.guild.id]
        except KeyError:
            return

        channel = await get_or_fetch_channel(self, int(data["logch"]))
        if channel:
            wMsg = data["wMsg"]
            
            try:    
                await channel.send(wMsg.format(mention = f"{member.mention}", servername = f"{member.guild.name}", membercount = f"{member.guild.member_count}", membername = f"{member}"))
            except KeyError:
                await channel.send('One or more of the placeholders you used in the welcome message was incorrect, or not a placeholder. To remove this message, please change it.')
            except ValueError:
                await channel.send('One or more of the placeholders you used in the welcome message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                await self.bot.sc.commit()
                self.bot.cache_welcome.pop(member.guild.id)
                logger.info(msg=f'Deleted welc channel b/c the bot did not have perms to speak - {member.guild} ({member.guild.id})')
                return



    @commands.Cog.listener()
    async def on_member_remove(self, member):
        #await asyncio.sleep(1)
        if member == self.bot.user:
            return
        server = member.guild.id
        
        
        try:   
            data = self.bot.cache_welcome[member.guild.id]
        except KeyError:
            return

        channel = await get_or_fetch_channel(self, int(data["logch"]))
        if channel:
            wMsg = data["bMsg"]
            
            try:    
                await channel.send(wMsg.format(mention = f"{member.mention}", servername = f"{member.guild.name}", membercount = f"{member.guild.member_count}", membername = f"{member}"))
            except KeyError:
                await channel.send('One or more of the placeholders you used in the goodbye message was incorrect, or not a placeholder. To remove this message, please change it.')
            except ValueError:
                await channel.send('One or more of the placeholders you used in the goodbye message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                await self.bot.sc.commit()
                self.bot.cache_welcome.pop(member.guild.id)
                logger.info(msg=f'Deleted welc channel b/c the bot did not have perms to speak - {member.guild} ({member.guild.id})')
                return 




def setup(bot):
	bot.add_cog(Welcome(bot))