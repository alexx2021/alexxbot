
import discord
import asyncio
import time
import random
from discord.ext import commands, tasks
from utils.utils import get_or_fetch_channel, get_or_fetch_member

BOT_ID = int(752585938630082641)
TEST_BOT_ID = int(715446479837462548)


class Giveaways(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    
    @commands.is_owner()
    @commands.command()
    async def dumpG(self, ctx):
        rows = await self.bot.rm.execute_fetchall("SELECT OID, guild_id, channel_id, message_id, user_id, future FROM giveaways")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @tasks.loop(seconds=12.0)
    async def check_giveaways(self):
        current_time1 = f"{int(time.time())}"
        rows = await self.bot.rm.execute_fetchall("SELECT guild_id, channel_id, message_id, user_id, future FROM giveaways WHERE future <= ?",(current_time1,),)

        while rows != []:
            await asyncio.sleep(2)
            
            toprow = rows[0]

            theguildID = toprow[0]
            thechannelid = toprow[1]
            themessageid = toprow[2]
            theuserid = toprow[3]
            
            bot = self.bot.get_user(BOT_ID)
            try:
                guildchannel = await get_or_fetch_channel(self, thechannelid)
                message = await guildchannel.fetch_message(themessageid)
                
                users = await message.reactions[0].users().flatten()
            except:

                await self.bot.rm.execute("DELETE FROM giveaways WHERE message_id = ?",(themessageid,))
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

                await message.channel.send(f"**Congrats {winner.mention}!**\nPlease contact <@{theuserid}> about your prize.")                                       

            await self.bot.rm.execute("DELETE FROM giveaways WHERE message_id = ?",(themessageid,))
            await self.bot.rm.commit()
            
            current_time = f"{int(time.time())}"
            rows = await self.bot.rm.execute_fetchall("SELECT guild_id, channel_id, message_id, user_id, future FROM giveaways WHERE future <= ?",(current_time,),)
    
    @check_giveaways.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Giveaways(bot))