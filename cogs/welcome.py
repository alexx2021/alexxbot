import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import has_permissions


class Welcome(commands.Cog):
    def __init__(self, client):
        self.client = client    

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
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
                    desc = 'Please enter your desired **welcome** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}` and, `{membercount}` are available.'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)

                    welcomeM = await self.client.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(f'Welcome message was **{len(wMsg)}** chars long, but it cannot be longer than 1024.')
                    
                    desc = 'Please enter your desired **goodbye** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}` and, `{membercount}` are available.'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)

                    goodbyeM = await self.client.wait_for('message', check=check, timeout=120)
                    
                    bMsg = goodbyeM.content
                    if len(bMsg) >= 1024:
                        return await ctx.send(f'Goodbye message was **{len(bMsg)}** chars long, but it cannot be longer than 1024.')
                
                except asyncio.exceptions.TimeoutError:
                    return await ctx.send(f'Message creation timed out. Please try again.')

                
                self.bot.sc.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, log_channel, wMsg, bMsg))
                self.bot.sc.commit()
                await ctx.send(f'Done! Welcome/goodbye channel set to {channel.mention}.')

            else:
                rows2 = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),)
                if rows2 != []:

                    self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                    self.bot.sc.commit()
                    await ctx.send('Welcome/goodbye channel has been reset. Run the command again to set the new channel.')

        if channel is None:
            local_log_channel = ctx.channel.id
            rows = self.c.execute("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server_id,),).fetchall()
            
            if rows == []:
                
                try:
                    desc = 'Please enter your desired **welcome** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}` and, `{membercount}` are available.'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)
                    
                    welcomeM = await self.client.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(f'Welcome message was **{len(wMsg)}** chars long, but it cannot be longer than 1024.')
                    
                    desc = 'Please enter your desired **goodbye** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}` and, `{membercount}` are available.'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)

                    goodbyeM = await self.client.wait_for('message', check=check, timeout=120)
                    
                    bMsg = goodbyeM.content
                    if len(bMsg) >= 1024:
                        return await ctx.send(f'Goodbye message was **{len(bMsg)}** chars long, but it cannot be longer than 1024.')
                
                except asyncio.exceptions.TimeoutError:
                    return await ctx.send(f'Message creation timed out. Please try again.')
                
                
                
                self.c.execute("INSERT INTO welcome VALUES(?, ?, ?, ?)", (server_id, local_log_channel, wMsg, bMsg))
                self.conn.commit()
                await ctx.send(f'Done! Welcome/goodbye channel set to {ctx.channel.mention}.')

            else:
                rows2 = self.c.execute("SELECT server_id FROM welcome WHERE server_id = ?",(server_id,),).fetchall()
                if rows2 != []:

                    self.c.execute("DELETE FROM welcome WHERE server_id = ?",(server_id,))
                    self.conn.commit()
                    await ctx.send('Welcome/goodbye channel has been reset. Run the command again to set the new channel.')


    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpW(self, ctx):
        rows = self.c.execute("SELECT server_id, log_channel, wMsg, bMsg FROM welcome").fetchall()
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def delwelcome(self, ctx):
        guild = ctx.guild.id
        self.c.execute("DELETE FROM welcome WHERE server_id = ?",(guild,))
        self.conn.commit()
        
        await ctx.channel.send('done.')


    #removes guild data if not in server anymore
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await asyncio.sleep(1)
        server = guild.id

        rows = self.c.execute("SELECT server_id FROM welcome WHERE server_id = ?",(server,),).fetchall()
        if rows != []:
            self.c.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
            self.conn.commit()
            return





    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        server = member.guild.id
        rows = self.c.execute("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server,),).fetchall()
        if rows != []:
            toprow = rows[0] 
            logCH = toprow[1]
            wMsg = toprow[2]
            channel = discord.utils.get(member.guild.channels, id=logCH)
            if not channel:
                return
            try:
                await channel.send(wMsg.format(mention = f"{member.mention}", servername = f"{member.guild.name}", membercount = f"{member.guild.member_count}", membername = f"{member}"))
            except KeyError:
                await channel.send('One or more of the placeholders you used in the welcome message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                server = member.guild.id

                rows = self.c.execute("SELECT server_id FROM welcome WHERE server_id = ?",(server,),).fetchall()
                if rows != []:
                    self.c.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                    self.conn.commit()
                    print(f'deleted welcome data b/c no perms 2 speak for ({member.guild.id})')



    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member == self.client.user:
            return

        server = member.guild.id
        rows = self.c.execute("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server,),).fetchall()
        if rows != []:
            toprow = rows[0] 
            logCH = toprow[1]
            bMsg = toprow[3]
            
            channel = discord.utils.get(member.guild.channels, id=logCH)
            if not channel:
                return
            try:    
                await channel.send(bMsg.format(mention = f"{member.mention}", servername = f"{member.guild.name}", membercount = f"{member.guild.member_count}", membername = f"{member}"))
            except KeyError:
                await channel.send('One or more of the placeholders you used in the goodbye message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                server = member.guild.id

                rows = self.c.execute("SELECT server_id FROM welcome WHERE server_id = ?",(server,),).fetchall()
                if rows != []:
                    self.c.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                    self.conn.commit()
                    print(f'deleted welcome data b/c no perms 2 speak for ({member.guild.id})')

 




def setup(client):
	client.add_cog(Welcome(client))