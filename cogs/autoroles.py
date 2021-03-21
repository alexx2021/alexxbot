import discord
import asyncio
from discord.ext import commands




class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(hidden=True)
    async def setautorole(self, ctx, role: discord.Role):
        pass

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        pass

    @commands.Cog.listener()
    async def on_member_join(self, member):
        pass

        
def setup(bot):
	bot.add_cog(AutoRoles(bot))
