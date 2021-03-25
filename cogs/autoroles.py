import discord
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions, has_permissions




class Autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpar(self, ctx):
        roles = await self.bot.sc.execute_fetchall("SELECT * FROM autorole")
        print('-----------dump-----------')
        print(roles)
        print('--------------------------')
        print(self.bot.autorolecache)
        print('-----------dump-----------')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.pending:
            return
        else:
            if member.guild.me.guild_permissions.manage_roles:
                try:    
                    r = self.bot.autorolecache[f"{member.guild.id}"]
                except KeyError:
                    return
                role = discord.utils.get(member.guild.roles, id= int(r))
                if role:
                    if member.guild.me.top_role.position > role.position:
                        await member.add_roles(role, reason=f"Autorole.")




    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.bot:
            return
        if after.bot:
            return
        
        if after.pending is False:
            if before.guild.me.guild_permissions.manage_roles:
                try:    
                    r = self.bot.autorolecache[f"{before.guild.id}"]
                except KeyError:
                    return
                role = discord.utils.get(before.guild.roles, id= int(r))
                if role:
                    if after.guild.me.top_role.position > role.position:
                        await after.add_roles(role, reason=f"Delayed autorole.")


            
def setup(bot):
    bot.add_cog(Autorole(bot))
