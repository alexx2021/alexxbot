from utils import check_if_log, sendlog
import discord
import asyncio
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions




class AutoRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @bot_has_permissions(manage_roles=True)    
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.command(aliases=["autorole"])
    async def setautorole(self, ctx, role: discord.Role):
        await self.bot.wait_until_ready()
        
        auto = await self.bot.sc.execute_fetchall("SELECT * FROM autorole WHERE guild_id = ?",(ctx.guild.id,),)
        if auto:
            await self.bot.sc.execute("UPDATE autorole SET role_id = ? WHERE guild_id = ?",(role.id, ctx.guild.id,),)
            await self.bot.sc.commit()
            self.bot.autorolecache.update({f"{ctx.guild.id}" : f"{role.id}"})
        else:    
            await self.bot.sc.execute("INSERT INTO autorole VALUES (?, ?)",(ctx.guild.id, role.id),)
            await self.bot.sc.commit()
            self.bot.autorolecache.update({f"{ctx.guild.id}" : f"{role.id}"})
            
        e = discord.Embed(description = f'Set the autorole to {role.mention}', color = 0)
        await ctx.send(embed = e)

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
                        member.add_roles(role, reason=f"Autorole.")

            else:
                if await check_if_log(self, member.guild):
                    e = discord.Embed(description ='**Autorole assignment failed because I am missing permissions to manage roles.**', color = 0)
                    await sendlog(self, member.guild, e)



    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.pending is False:
            if before.guild.me.guild_permissions.manage_guild:
                try:    
                    r = self.bot.autorolecache[f"{before.guild.id}"]
                except KeyError:
                    return
                role = discord.utils.get(before.guild.roles, id= int(r))
                if role:
                    if after.guild.me.top_role.position > role.position:
                        after.add_roles(role, reason=f"Delayed autorole.")

            else:
                if await check_if_log(self, before.guild):
                    e = discord.Embed(description ='**Autorole assignment failed because I am missing permissions to manage roles.**', color = 0)
                    await sendlog(self, before.guild, e)

            
def setup(bot):
    bot.add_cog(AutoRoles(bot))
