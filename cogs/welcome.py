import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import has_permissions


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

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
                    desc = 'Please enter your desired **welcome** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}`, `{membercount}`, `{invitedby}`, and `{invitecount}` are available.\nPlease note that if you wish to use {invitedby} or {invitecount} you __MUST__ have a logging channel set'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)

                    welcomeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(f'Welcome message was **{len(wMsg)}** chars long, but it cannot be longer than 1024.')
                    
                    desc = 'Please enter your desired **goodbye** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}`, `{membercount}`, `{invitedby}`, and `{invitecount}` are available.\nPlease note that if you wish to use {invitedby} or {invitecount} you __MUST__ have a logging channel set'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)

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
                    desc = 'Please enter your desired **welcome** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}`, `{membercount}`, `{invitedby}`, and `{invitecount}` are available.\nPlease note that if you wish to use {invitedby} or {invitecount} you __MUST__ have a logging channel set'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)
                    
                    welcomeM = await self.bot.wait_for('message', check=check, timeout=120)
                    
                    wMsg = welcomeM.content
                    if len(wMsg) >= 1024:
                        return await ctx.send(f'Welcome message was **{len(wMsg)}** chars long, but it cannot be longer than 1024.')
                    
                    desc = 'Please enter your desired **goodbye** message. \nThe placeholders `{mention}`, `{membername}`, `{servername}`, `{membercount}`, `{invitedby}`, and `{invitecount}` are available.\nPlease note that if you wish to use {invitedby} or {invitecount} you __MUST__ have a logging channel set'
                    e = discord.Embed(description=desc, color=0x7289da)
                    await ctx.send(embed=e)

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


    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpW(self, ctx):
        rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def delwelcome(self, ctx):
        guild = ctx.guild.id
        await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(guild,))
        await self.bot.sc.commit()
        
        await ctx.channel.send('done.')


    #removes guild data if not in server anymore
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await asyncio.sleep(1)
        server = guild.id

        rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server,),)
        if rows != []:
            await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
            await self.bot.sc.commit()
            return



    ### on join
    # check db to see who invited them by checking the inv_by
    # if they were invited send a message to the channel with who invited them and that person's new inv count
    # if they were invited by 4, send the message and mention that the inviter could not be determined

    ### on leave 
    # check db to see who invited them, if its not 4, send who invited them and their new count
    # if it is 4, send message saying they left and bot doesnt know who invited them

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(0.25)
        server = member.guild.id
        rows1 = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server,),)
        if rows1 != []:
            gid = member.guild.id
            uid = member.id

            query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
            params = (gid, uid)
            rows = await self.bot.i.execute_fetchall(query, params)
            if rows != []:
                toprow = rows[0]
                userid = toprow[1]
                invcount = toprow[2]
                invby = toprow[3]

                if invby == 4:
                    user = str('???')
                    invcount = str('?')

                else:
                    user = self.bot.get_user(invby)
                    if not user:
                        await self.bot.fetch_user(invby)
                        print('fetched user for inv log on join msg')
                        
                    query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                    params = (gid, invby)
                    rows = await self.bot.i.execute_fetchall(query, params)
                    if rows != []:
                        toprow = rows[0]
                        invcount = toprow[2]
            else:
                user = str('???')
                invcount = str('?')     
                #end of inv tracking
       
            toprow1 = rows1[0] 
            logCH = toprow1[1]
            wMsg = toprow1[2]
            channel = discord.utils.get(member.guild.channels, id=logCH)
            if not channel:
                return
            try:
                await channel.send(wMsg.format(mention = f"{member.mention}", servername = f"{member.guild.name}", membercount = f"{member.guild.member_count}", membername = f"{member}", invitedby = f"{user}", invitecount = f"{invcount}"))
            except KeyError:
                await channel.send('One or more of the placeholders you used in the welcome message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                server = member.guild.id

                rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server,),)
                if rows != []:
                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                    await self.bot.sc.commit()
                    print(f'deleted welcome data b/c no perms 2 speak for ({member.guild.id})')



    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await asyncio.sleep(0.25)
        if member == self.bot.user:
            return
        

        server = member.guild.id
        rows1 = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, wMsg, bMsg FROM welcome WHERE server_id = ?",(server,),)
        if rows1 != []:
            gid = member.guild.id
            uid = member.id

            query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
            params = (gid, uid)
            rows = await self.bot.i.execute_fetchall(query, params)
            if rows != []:
                toprow = rows[0]
                userid = toprow[1]
                invcount = toprow[2]
                invby = toprow[3]

                if invby == 4:
                    user = str('???')
                    invcount = str('?')


                else:
                    user = self.bot.get_user(invby)
                    if not user:
                        user = await self.bot.fetch_user(invby)
                        print('fetched user for inv log on leave msg')
                        
                    query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                    params = (gid, invby)
                    rows = await self.bot.i.execute_fetchall(query, params)
                    if rows != []:
                        toprow = rows[0]
                        invcount = toprow[2]
            else:
                user = str('???')
                invcount = str('?')
                #end inv user fetcher


            toprow1 = rows1[0] 
            logCH = toprow1[1]
            bMsg = toprow1[3]
            
            channel = discord.utils.get(member.guild.channels, id=logCH)
            if not channel:
                return
            try:    
                await channel.send(bMsg.format(mention = f"{member.mention}", servername = f"{member.guild.name}", membercount = f"{member.guild.member_count}", membername = f"{member}", invitedby = f"{user}", invitecount = f"{invcount}"))
            except KeyError:
                await channel.send('One or more of the placeholders you used in the goodbye message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                server = member.guild.id

                rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server,),)
                if rows != []:
                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                    await self.bot.sc.commit()
                    print(f'deleted welcome data b/c no perms 2 speak for ({member.guild.id})')

 




def setup(bot):
	bot.add_cog(Welcome(bot))