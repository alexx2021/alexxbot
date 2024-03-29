import discord
from discord.ext import commands




class aR(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.is_owner()
    @commands.command()
    async def dumpar(self, ctx):
        async with self.bot.db.acquire() as connection:
            roles = await connection.fetch("SELECT * FROM autorole")
        print('-----------dump-----------')
        print(roles)
        print('--------------------------')
        print(self.bot.cache_autorole)
        print('-----------dump-----------')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.pending:
            return
        else:
            if member.guild.me.guild_permissions.manage_roles:
                try:    
                    r = self.bot.cache_autorole[member.guild.id]
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
        
        if before.pending is True:
            if after.pending is False:
                if before.guild.me.guild_permissions.manage_roles:
                    try:    
                        r = self.bot.cache_autorole[before.guild.id]
                    except KeyError:
                        return
                    role = discord.utils.get(before.guild.roles, id= int(r))
                    if role:
                        if after.guild.me.top_role.position > role.position:
                            await after.add_roles(role, reason=f"Delayed autorole.")


            
def setup(bot):
    bot.add_cog(aR(bot))
