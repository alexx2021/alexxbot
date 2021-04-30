import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import time
import datetime
import logging

logger = logging.getLogger('discord')



#Reminders Category
class Reminders(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
    
   

    @commands.is_owner()
    @commands.command()
    async def dumpR(self, ctx):
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM reminders")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @commands.is_owner()
    @commands.command()
    async def testrm(self, ctx):
        x = 0
        while x < 10:
            x = x+1
            await asyncio.sleep(0.5)
            future = int(time.time()+10)
            id = int(ctx.author.id)
            remindtext = str("test")
            msgid = ctx.message.id
            async with self.bot.db.acquire() as connection:
                await connection.execute("INSERT INTO reminders VALUES($1, $2, $3, $4)", id, x, future, remindtext)
            
                rows2 = await connection.fetch("SELECT * FROM reminders")
                print(rows2)
            
            await ctx.channel.send('done.')



    @tasks.loop(seconds=2.0)
    async def check_reminders(self):
        current_time1 = int(time.time())
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM reminders WHERE future <= $1",(current_time1))
        
        while rows:
            await asyncio.sleep(2)
            
            toprow = rows[0]
            theuserID = toprow["user_id"]
            themessagecontent = toprow["remindtext"]
            ctx_ = toprow["ctx_id"]

            try:
                user = self.bot.get_user(int(theuserID))
                if not user:
                    user = self.bot.fetch_user(int(theuserID))
                    logger.warn(msg="Fetched user for reminder.")
                #await user.send(f'You asked me to remind you about: **{themessagecontent}**')
                embed = discord.Embed(color=0x7289da)
                embed.title = f"You asked me to remind you about:" 
                embed.description = f'{themessagecontent}'
                embed.timestamp = datetime.datetime.utcnow()
                await user.send(embed=embed)
            except:
                pass
            
            async with self.bot.db.acquire() as connection:
                await connection.execute("DELETE FROM reminders WHERE ctx_id = $1", ctx_)
                
                current_time = int(time.time())
                rows = await connection.fetch("SELECT * FROM reminders WHERE future <= $1",(current_time))

    @check_reminders.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()






def setup(bot):
    bot.add_cog(Reminders(bot))