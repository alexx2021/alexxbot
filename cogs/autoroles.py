import discord
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions, has_permissions




class Autorole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)    
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.command(aliases=["autorole"],help='Sets the role that new users get on join. Respects the discord rule verification menu.')
    async def setautorole(self, ctx, role: discord.Role):
        await self.bot.wait_until_ready()
        if ctx.author.top_role.position <= role.position:
            return await ctx.send('Error. The role you chose is above your highest role.')
        if ctx.guild.me.top_role.position <= role.position:
            return await ctx.send('Error. The role you chose is above my highest role.')
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

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)    
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.command(help='Deletes the currently set autorole.')
    async def delautorole(self, ctx):
        try:
            self.bot.autorolecache.pop(f"{ctx.guild.id}")
        except IndexError:
            pass
        await self.bot.sc.execute("DELETE FROM autorole WHERE guild_id = ?",(ctx.guild.id,))
        await self.bot.sc.commit()
        e = discord.Embed(description = f'Autorole disabled.', color = 0)
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
