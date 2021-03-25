import discord
import sqlite3
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import has_permissions


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    


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




    ### on join
    # check db to see who invited them by checking the inv_by
    # if they were invited send a message to the channel with who invited them and that person's new inv count
    # if they were invited by 4, send the message and mention that the inviter could not be determined

    ### on leave 
    # check db to see who invited them, if its not 4, send who invited them and their new count
    # if it is 4, send message saying they left and bot doesnt know who invited them

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(1)
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
            except ValueError:
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
        await asyncio.sleep(1)
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
            except ValueError:
                await channel.send('One or more of the placeholders you used in the welcome message was incorrect, or not a placeholder. To remove this message, please change it.')
            except discord.errors.Forbidden:
                server = member.guild.id

                rows = await self.bot.sc.execute_fetchall("SELECT server_id FROM welcome WHERE server_id = ?",(server,),)
                if rows != []:
                    await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
                    await self.bot.sc.commit()
                    print(f'deleted welcome data b/c no perms 2 speak for ({member.guild.id})')

 




def setup(bot):
	bot.add_cog(Welcome(bot))