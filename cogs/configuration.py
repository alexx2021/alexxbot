import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import bot_has_permissions, has_permissions
import asyncio
    
class Configuration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.command(aliases=["changeprefix", "prefix"],help='Sets the server prefix.')
    async def setprefix(self, ctx, prefix: str):
        await self.bot.wait_until_ready()
        if len(prefix) > 8:
            return await ctx.send('Prefix is too long.')
        
        custom = await self.bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(ctx.guild.id,),)
        if custom:
            await self.bot.pr.execute("UPDATE prefixes SET prefix = ? WHERE guild_id = ?",(prefix, ctx.guild.id,),)
            await self.bot.pr.commit()
            self.bot.prefixes.update({f"{ctx.guild.id}" : f"{prefix}"})
        else:    
            await self.bot.pr.execute("INSERT INTO prefixes VALUES (?, ?)",(ctx.guild.id, prefix),)
            await self.bot.pr.commit()
            self.bot.prefixes.update({f"{ctx.guild.id}" : f"{prefix}"})
            
        e = discord.Embed(description = f'Set prefix to `{prefix}`', color = 0)
        await ctx.send(embed = e)
    
    
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 15, commands.BucketType.guild)
    @commands.command(help='Use this to set your logging channel!', hidden=False)
    async def setlogchannel(self, ctx, channel: discord.TextChannel=None):
        server_id = ctx.guild.id
        
        if channel is not None:
                
                log_channel = channel.id
                null = str('null')
                rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server_id,),)
                
                if rows == []:
                    self.bot.logcache.update({f"{ctx.guild.id}" : f"{log_channel}"})

                    await self.bot.sc.execute("INSERT INTO logging VALUES(?, ?, ?)", (server_id, log_channel, null))
                    await self.bot.sc.commit()
                    await ctx.send(f'Done! Logging channel set to {channel.mention}.')

                else:
                    rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM logging WHERE server_id = ?",(server_id,),)
                    if rows != []:
                        try:
                            self.bot.logcache.pop(f"{ctx.guild.id}")
                        except IndexError:
                            pass
                        await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server_id,))
                        await self.bot.sc.commit()
                        await ctx.send('Logging channel has been reset. Run the command again to set the new channel.')

        if channel is None:
                local_log_channel = ctx.channel.id
                null = str('null')
                rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server_id,),)
                
                if rows == []:
                    self.bot.logcache.update({f"{ctx.guild.id}" : f"{local_log_channel}"})

                    await self.bot.sc.execute("INSERT INTO logging VALUES(?, ?, ?)", (server_id, local_log_channel, null))
                    await self.bot.sc.commit()
                    await ctx.send(f'Done! Logging channel set to {ctx.channel.mention}.')

                else:
                    rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM logging WHERE server_id = ?",(server_id,),)
                    if rows != []:
                        try:
                            self.bot.logcache.pop(f"{ctx.guild.id}")
                        except IndexError:
                            pass
                        await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server_id,))
                        await self.bot.sc.commit()
                        await ctx.send('Logging channel has been reset. Run the command again to set the new channel.')

    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.guild)
    @commands.command(help='Use this to set your welcome/goodbye channel!', hidden=False)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel=None):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        server_id = ctx.guild.id
        
        if channel is not None:
            log_channel = channel.id
            rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server_id,),)
            
            
            if rows == []:
                try:
                    embed=discord.Embed(title="Please enter your desired WELCOME message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)

                    welcomeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(f'Welcome message was **{len(wMsg)}** chars long, but it cannot be longer than 1024.')
                    
                    embed=discord.Embed(title="Please enter your desired GOODBYE message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)

                    goodbyeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    bMsg = goodbyeM.content
                    if len(bMsg) >= 1024:
                        return await ctx.send(f'Goodbye message was **{len(bMsg)}** chars long, but it cannot be longer than 1024.')
                
                except asyncio.exceptions.TimeoutError:
                    return await ctx.send(f'Message creation timed out. Please try again.')

                
                await self.bot.sc.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, log_channel, wMsg, bMsg))
                await self.bot.sc.commit()
                await ctx.send(f'Done! Welcome/goodbye channel set to {channel.mention}.')

            else:
                rows2 = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),)
                if rows2 != []:

                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                    await self.bot.sc.commit()
                    await ctx.send('Welcome/goodbye channel has been reset. Run the command again to set the new channel.')

        if channel is None:
            local_log_channel = ctx.channel.id
            rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server_id,),)
            
            if rows == []:
                
                try:
                    embed=discord.Embed(title="Please enter your desired WELCOME message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)
                    
                    welcomeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(f'Welcome message was **{len(wMsg)}** chars long, but it cannot be longer than 1024.')
                    
                    embed=discord.Embed(title="Please enter your desired GOODBYE message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)

                    goodbyeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    bMsg = goodbyeM.content
                    if len(bMsg) >= 1024:
                        return await ctx.send(f'Goodbye message was **{len(bMsg)}** chars long, but it cannot be longer than 1024.')
                
                except asyncio.exceptions.TimeoutError:
                    return await ctx.send(f'Message creation timed out. Please try again.')
                
                
                
                await self.bot.sc.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, local_log_channel, wMsg, bMsg))
                await self.bot.sc.commit()
                await ctx.send(f'Done! Welcome/goodbye channel set to {ctx.channel.mention}.')

            else:
                rows2 = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),)
                if rows2 != []:

                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                    await self.bot.sc.commit()
                    await ctx.send('Welcome/goodbye channel has been reset. Run the command again to set the new channel.')

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

def setup(bot):
	bot.add_cog(Configuration(bot))
