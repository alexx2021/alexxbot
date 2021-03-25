import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import time
import datetime





#Reminders Category
class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
    
   

    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpR(self, ctx):
        rows = await self.bot.rm.execute_fetchall("SELECT OID, id, future, remindtext FROM reminders")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def testrm(self, ctx):
        x = 0
        while x < 10:
            x = x+1
            await asyncio.sleep(0.25)
            future = int(time.time()+10)
            id = int(ctx.author.id)
            remindtext = str("test")
            await self.bot.rm.execute("INSERT INTO reminders VALUES(?, ?, ?)", (id, future, remindtext))
            await self.bot.rm.commit()
            
            await ctx.channel.send('done.')



    @tasks.loop(seconds=10.0)
    async def check_reminders(self):
        current_time1 = f"{int(time.time())}"
        rows = await self.bot.rm.execute_fetchall("SELECT OID, id, future, remindtext FROM reminders WHERE future <= ?",(current_time1,),)
        while rows != []:
            await asyncio.sleep(2)
            
            toprow = rows[0]
            therowID = toprow[0]
            theuserID = toprow[1]
            themessagecontent = toprow[3]

            try:
                user = self.bot.get_user(theuserID)
                if not user:
                    user = self.bot.fetch_user(theuserID)
                    print('fetched user for reminder because get did not work')
                #await user.send(f'You asked me to remind you about: **{themessagecontent}**')
                embed = discord.Embed(color=0x7289da)
                embed.title = f"You asked me to remind you about:" 
                embed.description = f'{themessagecontent}'
                embed.timestamp = datetime.datetime.utcnow()
                await user.send(embed=embed)
            except:
                pass

            TRID = f'{int(therowID)}'
            await self.bot.rm.execute("DELETE FROM reminders WHERE OID = ?",(TRID,))
            await self.bot.rm.commit()
            
            current_time = f"{int(time.time())}"
            rows = await self.bot.rm.execute_fetchall("SELECT OID, id, future, remindtext FROM reminders WHERE future <= ?",(current_time,),)

    @check_reminders.before_loop
    async def wait(self):
        await self.bot.wait_until_ready()






def setup(bot):
    bot.add_cog(Reminders(bot))