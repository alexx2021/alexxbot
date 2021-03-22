import discord
from discord.ext import commands
from discord.ext import tasks
import sqlite3
import asyncio
import time
import datetime





#Reminders Category
class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()
    
    
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.command(help='Reminds you about something after the time you choose! \n\n __timeinput__: 1 second --> 1s, 1 minute --> 1m, 1 hour --> 1h, 1 day --> 1d \nChoose ONE time unit in the command.', aliases=["rm","remind"])
    async def remindme(self, ctx,  timeinput, *, text):
        seconds = 0
        try: 
            if timeinput.lower().endswith("d"):
                seconds += int(timeinput[:-1]) * 60 * 60 * 24
                counter = f"**{seconds // 60 // 60 // 24} day(s)**"
            if timeinput.lower().endswith("h"):
                seconds += int(timeinput[:-1]) * 60 * 60
                counter = f"**{seconds // 60 // 60} hour(s)**"
            elif timeinput.lower().endswith("m"):
                seconds += int(timeinput[:-1]) * 60
                counter = f"**{seconds // 60} minute(s)**"
            elif timeinput.lower().endswith("s"):
                seconds += int(timeinput[:-1])
                counter = f"**{seconds} second(s)**"
            
            if seconds < 10:
                await ctx.send(f"Time must not be less than 10 seconds.")
                return
            if seconds > 7776000:
                await ctx.send(f"Time must not be more than 90 days")
                return
            if len(text) > 1900:
                await ctx.send(f"The text you provided is too long.")
                return
        except ValueError:
            return await ctx.send('Please check your time formatting and try again. s|m|h|d are valid time unit arguments.')
        
        future = int(time.time()+seconds)
        id = int(ctx.author.id)
        remindtext = text
        #await ctx.send(f'{future-seconds} = now, {int(time.time()+seconds)} = future time, {remindtext} = content  ')

        rows3 = await self.bot.rm.execute_fetchall("SELECT OID, id, future, remindtext FROM reminders WHERE id = ?",(id,),)
        if rows3 != []:
            try:
                if rows3[2]:
                    return await ctx.send(f'{ctx.author.mention}, you cannot have more than 3 reminders at once!')
            except IndexError:
                pass

        await self.bot.rm.execute("INSERT INTO reminders VALUES(?, ?, ?)", (id, future, remindtext))
        await self.bot.rm.commit()
        

        e = discord.Embed(description=f"{ctx.author.mention}, I will remind you of `{text}` in {counter}.", color = 0x7289da)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)
   

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