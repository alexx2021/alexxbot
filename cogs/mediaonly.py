import discord
import asyncio
from discord.ext import commands



class mediaOnly(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            self.bot.cache_mediaonly[message.guild.id][message.channel.id]
        except KeyError:
            return
        if not message.attachments:
            if not message.author.bot:
                if not message.author.guild_permissions.manage_messages:

                    #perms = message.channel.permissions_for(message.guild.me)

                    if message.guild.me.guild_permissions.manage_messages:# and perms.send_messages:
                        await message.delete()
                        #await asyncio.sleep(0.25)
                        #await message.channel.send(f'{message.author.mention}, this is a __media only__ channel!', delete_after = 4)



def setup(bot):
	bot.add_cog(mediaOnly(bot))