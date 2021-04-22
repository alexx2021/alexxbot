from utils.utils import check_if_log
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import bot_has_permissions, has_permissions
import asyncio
    
class Configuration(commands.Cog):
    """🛠️ Commands to configure the bot's features for your server"""
    def __init__(self, bot):
        self.bot = bot    

    @has_permissions(manage_messages=True)
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='View all of the settings for this guild in one place.', aliases=['db', 'dash'])
    async def dashboard(self, ctx):
        e = discord.Embed(title=f'Dashboard for {ctx.guild.name}', 
        color=discord.Color.blurple(),
            ).set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        async def _log():
            if await check_if_log(self, ctx.guild):
                ch = self.bot.logcache[f"{ctx.guild.id}"]
                return f"<:on1:834549521148411994> <#{int(ch)}>"
            else:
                return "<:off:834549474100641812>"
        async def _autorole():
            try:
                r = self.bot.autorolecache[f"{ctx.guild.id}"]
                return f"<:on1:834549521148411994> <@&{int(r)}>"
            except KeyError:
                return "<:off:834549474100641812>"
        async def _welcomech():
            try:   
                data = self.bot.welcomecache[f"{ctx.guild.id}"]
                logch = data["logch"]
                return f"<:on1:834549521148411994> <#{int(logch)}>"
            except KeyError:
                return "<:off:834549474100641812>"
        async def _levels():
            try:
                enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
                if 'TRUE' in enabled:
                    return "<:on1:834549521148411994>"
                else:
                    return "<:off:834549474100641812>"
            except KeyError:
                return "<:off:834549474100641812>"  
        async def _levelmessages():
            try:
                enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
                if 'TRUE' in enabled:
                    pass
                else:
                    return "<:off:834549474100641812>"
            except KeyError:
                return "<:off:834549474100641812>"  

            try:
                if 'TRUE' in self.bot.arelvlmsg[ctx.guild.id]:
                    return "<:on1:834549521148411994>"
                else:
                    return "<:off:834549474100641812>"  
            except KeyError:
                return "<:off:834549474100641812>" 
        async def _noxpch():
            try:
                enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
                if 'TRUE' in enabled:
                    pass
                else:
                    return "<:off:834549474100641812>"
            except KeyError:
                return "<:off:834549474100641812>"  

            try:
                l = '<:on1:834549521148411994>\n'
                for key in self.bot.xpignoredchannels[ctx.guild.id].items():
                    l += f'<#{key[0]}>\n'
                return f"{l}"      
            except KeyError:
                return "<:off:834549474100641812>"
        async def _roleRewards():
            try:
                enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
                if 'TRUE' in enabled:
                    pass
                else:
                    return "<:off:834549474100641812>"
            except KeyError:
                return "<:off:834549474100641812>"  

            try:
                l = '<:on1:834549521148411994>\n'
                for key in self.bot.xproles[ctx.guild.id].items():
                    l += f'Level {key[0]}: <@&{key[1]}>\n'
                return f"{l}"      
            except KeyError:
                return "<:off:834549474100641812>"








        e.add_field(name='General settings', 
        value=f'*Prefix:* \n`{ctx.prefix}`' 
        + f'\n*Autorole:* \n{await _autorole()}'
        + f'\n*Log channel:* \n{await _log()}'
        + f'\n*Welcome/Goodbye channel:* \n{await _welcomech()}'
            )

        e.add_field(name='Leveling settings', 
        value=f'*Leveling system:* \n{await _levels()}' 
        + f'\n*Leveling messages:* \n{await _levelmessages()}'
        + f'\n*No-XP channels:* \n{await _noxpch()}'
        + f'\n*Role rewards:* \n{await _roleRewards()}'
            )
        await ctx.send(embed=e)

    @has_permissions(manage_guild=True)
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @commands.command(aliases=["changeprefix", "prefix"],help='Sets the server prefix.')
    async def setprefix(self, ctx, prefix: str):
        await self.bot.wait_until_ready()
        error = '<a:x_:826577785173704754> Prefix is too long! Please try again with something shorter.'
        if len(prefix) > 8:
            return await ctx.send(error)
        
        custom = await self.bot.pr.execute_fetchall("SELECT guild_id, prefix FROM prefixes WHERE guild_id = ?",(ctx.guild.id,),)
        if custom:
            await self.bot.pr.execute("UPDATE prefixes SET prefix = ? WHERE guild_id = ?",(prefix, ctx.guild.id,),)
            await self.bot.pr.commit()
            self.bot.prefixes.update({f"{ctx.guild.id}" : f"{prefix}"})
        else:    
            await self.bot.pr.execute("INSERT INTO prefixes VALUES (?, ?)",(ctx.guild.id, prefix),)
            await self.bot.pr.commit()
            self.bot.prefixes.update({f"{ctx.guild.id}" : f"{prefix}"})
            
        e = f'<a:check:826577847023829032> Set prefix to `{prefix}`'
        await ctx.send(e)

    @commands.group(help='Use this to manage chat leveling settings.')
    async def levels(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `toggle`, `togglemessages`, `addrole`, `delrole`, `ignorechannel`, `unignorechannel`.')


    @levels.command(help='Set certain roles to be given when a user gets to a certain level.')
    @commands.cooldown(3, 10, commands.BucketType.user)
    @has_permissions(manage_guild=True)
    @commands.guild_only()
    async def addrole(self, ctx, level: int, role: discord.Role):
        if level <= 0 or not (str(level).isnumeric()):
            return await ctx.send('<a:x_:826577785173704754> Level must be greater than zero and a whole number.')
        if ctx.author.top_role.position <= role.position:
            return await ctx.send('<a:x_:826577785173704754> The role you chose is above your highest role.')
        if ctx.guild.me.top_role.position <= role.position:
            return await ctx.send('<a:x_:826577785173704754> The role you chose is above my highest role.')

        query = 'SELECT * FROM levelrewards WHERE guild_id = ? AND level = ?' 
        gid = ctx.guild.id
        params = (gid, level)
        guild = await self.bot.sc.execute_fetchall(query, params)
        try:
            if guild[9]:
                return await ctx.send('<a:x_:826577785173704754> You are only allowed to create 10 role rewards per guild.')
        except IndexError:
            pass
        if guild:
            query = 'UPDATE levelrewards SET role_id = ? WHERE guild_id = ? AND level = ?'
            params = (role.id, gid, level)
            await self.bot.sc.execute(query, params)
            await self.bot.sc.commit()
            await ctx.send(f'<a:check:826577847023829032> The {role.mention} role will now be given to people who obtain level {level}!')
        else:
            await self.bot.sc.execute('INSERT INTO levelrewards VALUES(?,?,?)',(gid, level, role.id))
            await self.bot.sc.commit()
            await ctx.send(f'<a:check:826577847023829032> The {role.mention} role will now be given to people who obtain level {level}!')
        try:
            enabled = self.bot.xproles[ctx.guild.id]
            if enabled:
                self.bot.xproles[ctx.guild.id].update({level: role.id})
        except KeyError:
            self.bot.xproles.update({ctx.guild.id: {level: role.id}})

    @levels.command(help='Delete role reward settings')
    @commands.cooldown(3, 10, commands.BucketType.user)
    @has_permissions(manage_guild=True)
    @commands.guild_only()
    async def delrole(self, ctx, level: int):
        if level <= 0 or not (str(level).isnumeric()):
            return await ctx.send('<a:x_:826577785173704754> Level must be greater than zero and a whole number.')
        try:
            self.bot.xproles[ctx.guild.id].pop(level)
        except KeyError:
            return await ctx.send('<a:x_:826577785173704754> There is no role reward assigned to this level.')

        query = 'DELETE FROM levelrewards WHERE guild_id = ? AND level = ?' 
        gid = ctx.guild.id
        params = (gid, level)
        await self.bot.sc.execute(query, params)
        await self.bot.sc.commit()
        await ctx.send(f'<a:check:826577847023829032> The role reward assigned to level {level} was deleted.')
    
        



    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @levels.command(help='Disable XP in certain channels.')
    async def ignorechannel(self, ctx: commands.Context):
        on = f'<a:check:826577847023829032> XP will no longer be granted in {ctx.channel.mention}!'
        err = '<a:x_:826577785173704754> This channel is already ignored by the xp system.'
        
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send('<a:x_:826577785173704754> This guild does not have xp enabled! Enable it with the `levels toggle` command!')
        except KeyError:
            return await ctx.send('<a:x_:826577785173704754> This guild does not have xp enabled! Enable it with the `levels toggle` command!')  

        try:
            ignored = self.bot.xpignoredchannels[ctx.guild.id][ctx.channel.id]
            if ignored:
                return await ctx.send(err)
        except KeyError:
            pass

        try:
            keys = self.bot.xpignoredchannels[ctx.guild.id]
            counter = 0
            for key in keys.items():
                counter += 1
            if counter >= 10:
                return await ctx.send('You have reached the maximum number of ignored channels you can set (10).')
        except KeyError:
            pass

        try:    
            self.bot.xpignoredchannels[ctx.guild.id][ctx.channel.id] = ctx.channel.id
        except KeyError:
            #print('ke')
            di = {ctx.channel.id: ctx.channel.id}
            self.bot.xpignoredchannels[ctx.guild.id] = di

        await self.bot.sc.execute('INSERT INTO ignoredchannels VALUES(?,?)',(ctx.guild.id, ctx.channel.id))
        await self.bot.sc.commit()
        return await ctx.send(on)

    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @levels.command(help='Re-enable XP in channels that were "ignored"')
    async def unignorechannel(self, ctx: commands.Context):
        on = f'<a:check:826577847023829032> XP will now be granted in {ctx.channel.mention}!'
        err = '<a:x_:826577785173704754> This channel is not ignored by the xp system!'
        
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send('<a:x_:826577785173704754> This guild does not have xp enabled! Enable it with the `levels toggle` command!')
        except KeyError:
            return await ctx.send('<a:x_:826577785173704754> This guild does not have xp enabled! Enable it with the `levels toggle` command!')  

        try:    
            self.bot.xpignoredchannels[ctx.guild.id].pop(ctx.channel.id)
        except KeyError:
            return await ctx.send(err)

        query = 'DELETE FROM ignoredchannels WHERE guild_id = ? AND channel_id = ?' 
        gid = ctx.guild.id
        cid = ctx.channel.id
        params = (gid, cid)
        await self.bot.sc.execute(query, params)
        await self.bot.sc.commit()

        
        return await ctx.send(on)



    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @levels.command(help='Enable/disable chat level messages.')
    async def togglemessages(self, ctx: commands.Context):
        on = '<a:check:826577847023829032> Enabled leveling messages!'
        off = '<a:check:826577847023829032> Disabled leveling messages!'
        
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send('<a:x_:826577785173704754> This guild does not have xp enabled! Enable it with the `levels toggle` command!')
        except KeyError:
            return await ctx.send('<a:x_:826577785173704754> This guild does not have xp enabled! Enable it with the `levels toggle` command!')  
        
        
        guild = await self.bot.xp.execute_fetchall("SELECT * FROM lvlsenabled WHERE guild_id = ?",(ctx.guild.id,))
        if guild:
            if guild[0][1] == 'TRUE':
                await self.bot.xp.execute('UPDATE lvlsenabled SET enabled = ? WHERE guild_id = ?',('FALSE',ctx.guild.id))
                await self.bot.xp.commit()
                self.bot.arelvlmsg.update({ctx.guild.id: 'FALSE'})
                await ctx.send(off)
            else:
                await self.bot.xp.execute('UPDATE lvlsenabled SET enabled = ? WHERE guild_id = ?',('TRUE',ctx.guild.id))
                await self.bot.xp.commit()
                self.bot.arelvlmsg.update({ctx.guild.id: 'TRUE'})
                await ctx.send(on)
        else:
            await self.bot.xp.execute('INSERT INTO lvlsenabled VALUES(?,?)',(ctx.guild.id,'TRUE'))
            await self.bot.xp.commit()
            self.bot.arelvlmsg.update({ctx.guild.id: 'TRUE'})
            await ctx.send(on)

    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @levels.command(help="Enable/disable chat levels on your server.")
    @has_permissions(manage_guild=True)
    @bot_has_permissions(add_reactions=True)
    async def toggle(self, ctx):
        on = '<a:check:826577847023829032> Enabled chat leveling!'
        off = '<a:check:826577847023829032> Done. Chat levels for this server are now disabled.'
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
                        
                        await ctx.send(off)
                    else:
                        await ctx.send('Operation cancelled.')
                
                if guild[0][1] == 'FALSE':
                    await self.bot.xp.execute('UPDATE chatlvlsenabled SET enabled = ? WHERE guild_id = ?',('TRUE',ctx.guild.id))
                    await self.bot.xp.commit()
                    self.bot.arelvlsenabled.update({f"{ctx.guild.id}": f"TRUE"})
                    await ctx.send(on)

            else:
                await self.bot.xp.execute('INSERT INTO chatlvlsenabled VALUES(?,?)',(ctx.guild.id,'TRUE'))
                await self.bot.xp.commit()
                self.bot.arelvlsenabled.update({f"{ctx.guild.id}": f"TRUE"})
                await ctx.send(on)
        
        except asyncio.exceptions.TimeoutError:
            return await ctx.send('You did not react in time.')
    
    
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 15, commands.BucketType.guild)
    @commands.command(help='Use this to set your logging channel!', hidden=False)
    async def setlogchannel(self, ctx):
        server_id = ctx.guild.id
        
        on = f'<a:check:826577847023829032> Logging channel set to {ctx.channel.mention}.'
        
        off = '<a:check:826577847023829032> Logging channel has been reset. Run the command again to set the new channel.'

        
        local_log_channel = ctx.channel.id
        null = str('null')
        rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server_id,),)
        
        if rows == []:
            self.bot.logcache.update({f"{ctx.guild.id}" : f"{local_log_channel}"})

            await self.bot.sc.execute("INSERT INTO logging VALUES(?, ?, ?)", (server_id, local_log_channel, null))
            await self.bot.sc.commit()
            await ctx.send(on)

        else:
            rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM logging WHERE server_id = ?",(server_id,),)
            if rows != []:
                try:
                    self.bot.logcache.pop(f"{ctx.guild.id}")
                except KeyError:
                    pass
                await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server_id,))
                await self.bot.sc.commit()
                await ctx.send(off)

    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.guild)
    @commands.command(help='Use this to set your welcome/goodbye channel!', hidden=False)
    async def setwelcomechannel(self, ctx):
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel
        
        lengthErrorHi = f'<a:x_:826577785173704754> Welcome message cannot be longer than 1024 chars.'
        lengthErrorBye = f'<a:x_:826577785173704754> Goodbye message cannot be longer than 1024 chars.'
    
        
        localON = f'<a:check:826577847023829032> Welcome/goodbye channel set to {ctx.channel.mention}.'
        
        off = '<a:check:826577847023829032> The welcome/goodbye channel has been reset. Run the command again to set the new channel.'
        
        server_id = ctx.guild.id
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
                    return await ctx.send(lengthErrorHi)
                
                embed=discord.Embed(title="Please enter your desired GOODBYE message.", color=0x7289da)
                embed.add_field(name="Placeholders:", value="`{mention}` `{membername}` `{servername}` `{membercount}`", inline=True)
                await ctx.send(embed=embed)

                goodbyeM = await self.bot.wait_for('message', check=check, timeout=120)
                
                bMsg = goodbyeM.content
                if len(bMsg) >= 1024:
                    return await ctx.send(lengthErrorBye)
            
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
            await ctx.send(localON)

        else:
            rows2 = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),)
            if rows2 != []:

                await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                await self.bot.sc.commit()
                try:
                    self.bot.welcomecache.pop(f"{ctx.guild.id}")
                except KeyError:
                    pass
                await ctx.send(off)



    @commands.group(help='Use this to manage autorole settings.')
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `remove`, `set`.')



    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)    
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @autorole.command(aliases=["autorole"],help='Sets the role that new users get on join. Respects the discord rule verification menu.')
    async def set(self, ctx, role: discord.Role):
        if ctx.author.top_role.position <= role.position:
            return await ctx.send('<a:x_:826577785173704754> The role you chose is above your highest role.')
        if ctx.guild.me.top_role.position <= role.position:
            return await ctx.send('<a:x_:826577785173704754> The role you chose is above my highest role.')
        auto = await self.bot.sc.execute_fetchall("SELECT * FROM autorole WHERE guild_id = ?",(ctx.guild.id,),)
        if auto:
            await self.bot.sc.execute("UPDATE autorole SET role_id = ? WHERE guild_id = ?",(role.id, ctx.guild.id,),)
            await self.bot.sc.commit()
            self.bot.autorolecache.update({f"{ctx.guild.id}" : f"{role.id}"})
        else:    
            await self.bot.sc.execute("INSERT INTO autorole VALUES (?, ?)",(ctx.guild.id, role.id),)
            await self.bot.sc.commit()
            self.bot.autorolecache.update({f"{ctx.guild.id}" : f"{role.id}"})
            
        e = f'<a:check:826577847023829032> Set the autorole to {role.mention}'
        await ctx.send(e)

    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles=True)    
    @commands.cooldown(2, 10, commands.BucketType.guild)
    @autorole.command(help='Deletes the currently set autorole.')
    async def remove(self, ctx):
        auto = await self.bot.sc.execute_fetchall("SELECT * FROM autorole WHERE guild_id = ?",(ctx.guild.id,),)
        if auto:
            try:
                self.bot.autorolecache.pop(f"{ctx.guild.id}")
            except KeyError:
                pass
            await self.bot.sc.execute("DELETE FROM autorole WHERE guild_id = ?",(ctx.guild.id,))
            await self.bot.sc.commit()
            e = '<a:check:826577847023829032> Autorole disabled.'
            await ctx.send(e)
        else:
            try:
                self.bot.autorolecache.pop(f"{ctx.guild.id}")
            except KeyError:
                pass
            e = '<a:x_:826577785173704754> There is no autorole currently set up in this server.'
            await ctx.send(e)

    @commands.command(help='Enable/disable chat games that are automatically sent to the channel you use this command in!')
    @commands.cooldown(3, 10, commands.BucketType.user)
    @has_permissions(manage_guild=True)
    @commands.guild_only()
    async def autochatgames(self, ctx):
        try:
            if self.bot.autogames[ctx.guild.id]:
                if self.bot.autogames[ctx.guild.id]["ongoing"] == 0:
                    self.bot.autogames.pop(ctx.guild.id)
                    await self.bot.sc.execute('DELETE FROM autogames WHERE guild_id = ?',(ctx.guild.id,))
                    await self.bot.sc.commit()
                    return await ctx.send('<a:check:826577847023829032> Disabled auto chatgames.')
                else:
                    return await ctx.send('<a:x_:826577785173704754> You cannot disable this feature while there is an ongoing game')

        except KeyError:
            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel
            
            await ctx.send('Please enter the delay you would like between sending the chat games.')
            try:    
                msg = await self.bot.wait_for('message', check=check, timeout=30)
                if msg.content.isnumeric():
                    delayInMinutes = int(msg.content)

                    if delayInMinutes < 2:
                        return await ctx.send('<a:x_:826577785173704754> Delay cannot be less than 2 (minutes)!')
                    elif delayInMinutes >= 121:
                        return await ctx.send('<a:x_:826577785173704754> Delay cannot be greater than 120 (minutes)')
                    self.bot.autogames.update({ctx.guild.id : {"channel_id": ctx.channel.id, "lastrun": 0, "ongoing": 0, "delay": delayInMinutes}})
                    await self.bot.sc.execute('INSERT INTO autogames VALUES(?,?,?)',(ctx.guild.id, ctx.channel.id, delayInMinutes,))
                    await self.bot.sc.commit()
                    return await ctx.send(f'<a:check:826577847023829032> Enabled auto chatgames for this channel with a delay of {delayInMinutes} minutes.')
                else:
                    return await ctx.send('<a:x_:826577785173704754> Delay must be a whole, positive and valid number!')
            except asyncio.exceptions.TimeoutError:
                return await ctx.send('Operation timed out.')



def setup(bot):
	bot.add_cog(Configuration(bot))
