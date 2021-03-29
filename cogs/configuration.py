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
        error = discord.Embed(color= discord.Color.red(), description = 'Prefix is too long! Please try again wth something shorter.', title= ":x: Error")
        if len(prefix) > 8:
            return await ctx.send(embed = error)
        
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
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='Enable/disable chat level messages.')
    async def togglelevelmessages(self, ctx: commands.Context):
        error = discord.Embed(description='This guild does not have xp enabled!\nEnable it with the `togglechatleveling` command!', color = discord.Color.red(), title= ":x: Error")
        
        on = discord.Embed(description = '**Enabled** leveling messages!', color = 0)
        on.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        off = discord.Embed(description = '**Disabled** leveling messages!', color = 0)
        off.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send(embed=error)
        except KeyError:
            return await ctx.send(embed=error)  
        
        
        guild = await self.bot.xp.execute_fetchall("SELECT * FROM lvlsenabled WHERE guild_id = ?",(ctx.guild.id,))
        if guild:
            if guild[0][1] == 'TRUE':
                await self.bot.xp.execute('UPDATE lvlsenabled SET enabled = ? WHERE guild_id = ?',('FALSE',ctx.guild.id))
                await self.bot.xp.commit()
                await ctx.send(embed = off)
            else:
                await self.bot.xp.execute('UPDATE lvlsenabled SET enabled = ? WHERE guild_id = ?',('TRUE',ctx.guild.id))
                await self.bot.xp.commit()
                await ctx.send(embed = on)
        else:
            await self.bot.xp.execute('INSERT INTO lvlsenabled VALUES(?,?)',(ctx.guild.id,'TRUE'))
            await self.bot.xp.commit()
            await ctx.send(embed = on)

    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.command(help="Enable/disable chat levels on your server.")
    @has_permissions(manage_guild=True)
    async def togglechatleveling(self, ctx):
        on = discord.Embed(description = '**Enabled** chat leveling!', color = 0)
        on.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        off = discord.Embed(description = 'Done. Chat levels for this server are now **disabled**.', color = 0)
        off.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        warn = discord.Embed(description = 'You are about to disable the leveling system for this server.\n__ALL DATA WILL BE LOST__.\nAre you sure?', color = discord.Color.red(), title = 'Warning')
        
        try:    
            guild = await self.bot.xp.execute_fetchall("SELECT * FROM chatlvlsenabled WHERE guild_id = ?",(ctx.guild.id,))
            if guild:
                if guild[0][1] == 'TRUE':
                    msg = await ctx.send(embed = warn)
                    await asyncio.sleep(0.25)
                    await msg.add_reaction("✅")
                    await asyncio.sleep(0.25)
                    await msg.add_reaction("❌")
                    reaction, person = await self.bot.wait_for(
                                    "reaction_add",
                                    timeout=60,
                                    check=lambda reaction, user: user == ctx.author
                                    and reaction.message.channel == ctx.channel)
                    
                    if str(reaction.emoji) == "✅":
                        query = 'DELETE FROM xp WHERE guild_id = ?' 
                        gid = ctx.guild.id
                        params = (gid,)
                        await self.bot.xp.execute(query, params)
                        await self.bot.xp.execute('UPDATE chatlvlsenabled SET enabled = ? WHERE guild_id = ?',('FALSE',ctx.guild.id))
                        await self.bot.xp.commit()
                        self.bot.arelvlsenabled.update({f"{ctx.guild.id}": f"FALSE"})
                        
                        await ctx.send(embed = off)
                    else:
                        await ctx.send('Operation cancelled.')
                
                if guild[0][1] == 'FALSE':
                    await self.bot.xp.execute('UPDATE chatlvlsenabled SET enabled = ? WHERE guild_id = ?',('TRUE',ctx.guild.id))
                    await self.bot.xp.commit()
                    self.bot.arelvlsenabled.update({f"{ctx.guild.id}": f"TRUE"})
                    await ctx.send(embed = on)

            else:
                await self.bot.xp.execute('INSERT INTO chatlvlsenabled VALUES(?,?)',(ctx.guild.id,'TRUE'))
                await self.bot.xp.commit()
                self.bot.arelvlsenabled.update({f"{ctx.guild.id}": f"TRUE"})
                await ctx.send(embed = on)
        
        except asyncio.exceptions.TimeoutError:
            return await ctx.send('You did not react in time.')
    
    
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 15, commands.BucketType.guild)
    @commands.command(help='Use this to set your logging channel!', hidden=False)
    async def setlogchannel(self, ctx, channel: discord.TextChannel=None):
        server_id = ctx.guild.id
        error = discord.Embed(description='I do not have permission to speak in that channel!', color = discord.Color.red(), title= ":x: Error")
        
        on = discord.Embed(description=f'Logging channel set to {channel.mention}.', color = 0)
        on.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        localON = discord.Embed(description=f'Logging channel set to {ctx.channel.mention}.', color = 0)
        localON.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        off = discord.Embed(description='Logging channel has been reset. Run the command again to set the new channel.', color = 0)
        off.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        if channel is not None:
            perms = channel.permissions_for(ctx.guild.me) #check to see if the bot can speak in the channel
            if not perms.send_messages:
                return await ctx.send(embed = error)
                
            log_channel = channel.id
            null = str('null')
            rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server_id,),)
            
            if rows == []:
                self.bot.logcache.update({f"{ctx.guild.id}" : f"{log_channel}"})

                await self.bot.sc.execute("INSERT INTO logging VALUES(?, ?, ?)", (server_id, log_channel, null))
                await self.bot.sc.commit()
                await ctx.send(embed = on)

            else:
                rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM logging WHERE server_id = ?",(server_id,),)
                if rows != []:
                    try:
                        self.bot.logcache.pop(f"{ctx.guild.id}")
                    except KeyError:
                        pass
                    await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server_id,))
                    await self.bot.sc.commit()
                    await ctx.send(embed = off)

        if channel is None:
                local_log_channel = ctx.channel.id
                null = str('null')
                rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server_id,),)
                
                if rows == []:
                    self.bot.logcache.update({f"{ctx.guild.id}" : f"{local_log_channel}"})

                    await self.bot.sc.execute("INSERT INTO logging VALUES(?, ?, ?)", (server_id, local_log_channel, null))
                    await self.bot.sc.commit()
                    await ctx.send(embed = localON)

                else:
                    rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM logging WHERE server_id = ?",(server_id,),)
                    if rows != []:
                        try:
                            self.bot.logcache.pop(f"{ctx.guild.id}")
                        except KeyError:
                            pass
                        await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server_id,))
                        await self.bot.sc.commit()
                        await ctx.send(embed = off)

    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.guild)
    @commands.command(help='Use this to set your welcome/goodbye channel!', hidden=False)
    async def setwelcomechannel(self, ctx, channel: discord.TextChannel=None):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
         #need to initialize this so python doesnt complain lol
        channel = ctx.channel
        error = discord.Embed(description='I do not have permission to speak in that channel!', color = discord.Color.red(), title= ":x: Error")
        lengthErrorHi = discord.Embed(description=f'Welcome message cannot be longer than 1024 chars.', color = discord.Color.red(), title= ":x: Error")
        lengthErrorBye = discord.Embed(description=f'Goodbye message cannot be longer than 1024 chars.', color = discord.Color.red(), title= ":x: Error")

        on = discord.Embed(description=f'Welcome/goodbye channel set to {channel.mention}.', color = 0)
        on.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        localON = discord.Embed(description=f'Welcome/goodbye channel set to {ctx.channel.mention}.', color = 0)
        localON.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        off = discord.Embed(description='The welcome/goodbye channel has been reset. Run the command again to set the new channel.', color = 0)
        off.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        
        server_id = ctx.guild.id
        
        if channel is not None:
            log_channel = channel.id
            perms = channel.permissions_for(ctx.guild.me) #check if the bot can speak in the channel it needs to 
            if not perms.send_messages:
                return await ctx.send(embed = error)
            
            rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server_id,),)
            
            
            if rows == []:
                try:
                    embed=discord.Embed(title="Please enter your desired WELCOME message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)

                    welcomeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(embed = lengthErrorHi)
                    
                    embed=discord.Embed(title="Please enter your desired GOODBYE message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)

                    goodbyeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    bMsg = goodbyeM.content
                    if len(bMsg) >= 1024:
                        return await ctx.send(embed = lengthErrorBye)
                
                except asyncio.exceptions.TimeoutError:
                    return await ctx.send(f'Message creation timed out. Please try again.')

                
                await self.bot.sc.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, log_channel, wMsg, bMsg))
                await self.bot.sc.commit()
                di = {
                "logch" : log_channel, 
                "wMsg" : wMsg,
                "bMsg" : bMsg
                        }
                self.bot.welcomecache.update({f'{ctx.guild.id}': di})                
                await ctx.send(embed = on)

            else:
                rows2 = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),)
                if rows2 != []:

                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                    await self.bot.sc.commit()
                    try:
                        self.bot.welcomecache.pop(f"{ctx.guild.id}")
                    except KeyError:
                        pass
                    await ctx.send(embed = off)

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
                        return await ctx.send(embed = lengthErrorHi)
                    
                    embed=discord.Embed(title="Please enter your desired GOODBYE message.", color=0x7289da)
                    embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                    await ctx.send(embed=embed)

                    goodbyeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    bMsg = goodbyeM.content
                    if len(bMsg) >= 1024:
                        return await ctx.send(embed = lengthErrorBye)
                
                except asyncio.exceptions.TimeoutError:
                    return await ctx.send(f'Message creation timed out. Please try again.')
                
                
                
                await self.bot.sc.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, local_log_channel, wMsg, bMsg))
                await self.bot.sc.commit()
                di = {
                "logch" : local_log_channel, 
                "wMsg" : wMsg,
                "bMsg" : bMsg
                        }
                self.bot.welcomecache.update({f'{ctx.guild.id}': di})                
                await ctx.send(embed = localON)

            else:
                rows2 = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),)
                if rows2 != []:

                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                    await self.bot.sc.commit()
                    try:
                        self.bot.welcomecache.pop(f"{ctx.guild.id}")
                    except KeyError:
                        pass
                    await ctx.send(embed = off)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)    
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.command(aliases=["autorole"],help='Sets the role that new users get on join. Respects the discord rule verification menu.')
    async def setautorole(self, ctx, role: discord.Role):
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
        auto = await self.bot.sc.execute_fetchall("SELECT * FROM autorole WHERE guild_id = ?",(ctx.guild.id,),)
        if auto:
            try:
                self.bot.autorolecache.pop(f"{ctx.guild.id}")
            except KeyError:
                pass
            await self.bot.sc.execute("DELETE FROM autorole WHERE guild_id = ?",(ctx.guild.id,))
            await self.bot.sc.commit()
            e = discord.Embed(description = f'Autorole disabled.', color = 0)
            await ctx.send(embed = e)
        else:
            try:
                self.bot.autorolecache.pop(f"{ctx.guild.id}")
            except KeyError:
                pass
            e = discord.Embed(description = f'There is no autorole currently set up in this server.', color = 0)
            await ctx.send(embed = e)

def setup(bot):
	bot.add_cog(Configuration(bot))
