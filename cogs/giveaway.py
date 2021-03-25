
import discord
import asyncio
import datetime
import time
import random
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import bot_has_permissions, has_permissions
from utils import get_or_fetch_channel, get_or_fetch_guild

BOT_ID = int(752585938630082641)
TEST_BOT_ID = int(715446479837462548)


class Giveaways(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    
    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpG(self, ctx):
        rows = await self.bot.rm.execute_fetchall("SELECT OID, guild_id, channel_id, message_id, user_id, future FROM giveaways")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @tasks.loop(seconds=12.0)
    async def check_giveaways(self):
        current_time1 = f"{int(time.time())}"
        rows = await self.bot.rm.execute_fetchall("SELECT OID, guild_id, channel_id, message_id, user_id, future FROM giveaways WHERE future <= ?",(current_time1,),)

        while rows != []:
            await asyncio.sleep(2)
            
            toprow = rows[0]

            therowID = toprow[0]
            theguildID = toprow[1]
            thechannelid = toprow[2]
            themessageid = toprow[3]
            theuserid = toprow[4]
            
            bot = self.bot.get_user(BOT_ID)
            try:
                theguild = await get_or_fetch_guild(self, theguildID)
                guildchannel = await get_or_fetch_channel(self, theguild, thechannelid)
                message = await guildchannel.fetch_message(themessageid)
                
                users = await message.reactions[0].users().flatten()
                author = await self.bot.fetch_user(theuserid)
            except:
                TRID = f'{int(therowID)}'
                await self.bot.rm.execute("DELETE FROM giveaways WHERE OID = ?",(TRID,))
                await self.bot.rm.commit()
                return
            try:
                users.pop(users.index(bot))
            except ValueError:
                pass
            #users.pop(users.index(author))

            if len(users) == 0:
                await message.channel.send("No winner was decided")
            else:
                winner = random.choice(users)

                await message.channel.send(f"**Congrats {winner.mention}!**\nPlease contact {author.mention} about your prize.")                                       

            TRID = f'{int(therowID)}'
            await self.bot.rm.execute("DELETE FROM giveaways WHERE OID = ?",(TRID,))
            await self.bot.rm.commit()
            
            current_time = f"{int(time.time())}"
            rows = await self.bot.rm.execute_fetchall("SELECT OID, guild_id, channel_id, message_id, user_id, future FROM giveaways WHERE future <= ?",(current_time,),)
    
    @check_giveaways.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Giveaways(bot))