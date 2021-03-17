import discord
import aiosqlite
import asyncio
import datetime
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions, has_permissions


class WelcomeInvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    


########################################################## relevant events

    ### on join
    # check db to see who invited them by checking the inv_by
    # if they were invited send a message to the channel with who invited them and that person's new inv count
    # if they were invited by 4, send the message and mention that the inviter could not be determined

    ### on leave 
    # check db to see who invited them, if its not 4, send who invited them and their new count
    # if it is 4, send message saying they left and bot doesnt know who invited them
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member == self.bot.user:
            return
        await asyncio.sleep(1)
        
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
                

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(1)
        
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





def setup(bot):
    bot.add_cog(WelcomeInvite(bot))
