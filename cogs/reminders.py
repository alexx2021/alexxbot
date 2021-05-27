import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import time
import datetime
import logging

from discord.ext.buttons import Paginator
from discord.ext.commands.core import bot_has_permissions

logger = logging.getLogger('discord')

class Pag(Paginator):
    async def teardown(self):
        try:
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass


#Reminders Category
class reminders(commands.Cog, command_attrs=dict(hidden=False)):
    """⏰ Never forget about something important"""
    def __init__(self, bot):
        self.bot = bot
        self.check_reminders.start()

    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.command(help='Reminds you about something after the time you choose!', aliases=["rm","remind"])
    async def remindme(self, ctx,  timeinput, *, text):
        err = f'<a:x_:826577785173704754> An error occurred. Please check the following:\n\n1. The time cannot be more than 2 years, or less than 10 seconds\n2. The text you input was absurdly long\n3. The formatting for the time might be incorrect. `s|m|h|d` are valid time unit arguments.\n\nExample: `_remindme 1h do the thing`'

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
                await ctx.send(err)
                return
            if seconds > 63072000:
                await ctx.send(err)
                return
            if len(text) > 1500:
                await ctx.send(err)
                return
        except ValueError:
            return await ctx.send(err)
        
        future = int(time.time()+seconds)
        id = int(ctx.author.id)
        remindtext = text
        #await ctx.send(f'{future-seconds} = now, {int(time.time()+seconds)} = future time, {remindtext} = content  ')

        async with self.bot.db.acquire() as connection:
            rows3 = await connection.fetch("SELECT * FROM reminders WHERE user_id = $1",(id))
            if rows3:
                try:
                    if rows3[100]:
                        return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention}, hmm it seems like you have 100 reminders... please join the support server and send a screenshot of this to Alexx to get the restriction removed.')
                except IndexError:
                    pass
            await connection.execute("INSERT INTO reminders VALUES($1, $2, $3, $4)", id, ctx.message.id, future, remindtext)
        

        await ctx.send(f"{ctx.author.mention}, I will remind you of `{text}` in {counter}. Reminder ID: {ctx.message.id}")


    @bot_has_permissions(add_reactions=True)
    @commands.cooldown(2, 6, commands.BucketType.user)
    @commands.command(help='Lists all active reminders.')
    async def listreminders(self, ctx):
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM reminders WHERE user_id = $1 ORDER BY future ASC", ctx.author.id)
            if not rows:
                return await ctx.send('You do not have any active reminders!')
            else:
                desc =[]
                for rank, record in enumerate(rows, start=1):
                    ctx_ = record["ctx_id"]
                    time_ = record["future"]
                    text = record["remindtext"]
                    secondsUntil = time_ - time.time()
                    daysUntil = round(secondsUntil / 86400,2)
                    hrUntil = round(secondsUntil / 3600,2)
                    minUntil = round(secondsUntil / 60,2)
                    if daysUntil > 1:
                        remaining = daysUntil
                        timeUnit = "d"
                        #print('1')
                    elif hrUntil > 1:
                        remaining = hrUntil
                        timeUnit = "h"
                        #print('2')
                    else:
                        remaining = minUntil
                        timeUnit = "m"
                        #print('3')




                    e=f"**{rank}**. ID: {ctx_} - {remaining}{timeUnit} remaining\n`{text[:250]}`"
                    desc.append(e)

                pager = Pag(
                    title=f"Reminders for {ctx.author}", 
                    colour=discord.Colour.blurple(),
                    timeout=15,
                    entries=desc,
                    length=5,
                )

                await pager.start(ctx)

    @commands.cooldown(5, 8, commands.BucketType.user)
    @commands.command(help='Cancel an already existing reminder.')
    async def cancelreminder(self, ctx, reminderID: int):
        async with self.bot.db.acquire() as connection:
            await connection.execute('DELETE FROM reminders WHERE ctx_id = $1 AND user_id = $2', reminderID, ctx.author.id)
        await ctx.send(f'<a:check:826577847023829032> Cancelled any reminders that belong to you with the ID `{reminderID}`.')



    # @commands.is_owner()
    # @commands.command(hidden=True)
    # async def testrm(self, ctx):
    #     x = 0
    #     while x < 10:
    #         x = x+1
    #         await asyncio.sleep(0.5)
    #         future = int(time.time()+10)
    #         id = int(ctx.author.id)
    #         remindtext = str("test")
    #         msgid = ctx.message.id
    #         async with self.bot.db.acquire() as connection:
    #             await connection.execute("INSERT INTO reminders VALUES($1, $2, $3, $4)", id, x, future, remindtext)
            
    #             rows2 = await connection.fetch("SELECT * FROM reminders")
    #             print(rows2)
            
    #         await ctx.channel.send('done.')



    @tasks.loop(seconds=10.0)
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
                    logger.warn(msg=f"Fetched user for reminder. u.{theuserID}")
                #await user.send(f'You asked me to remind you about: **{themessagecontent}**')
                embed = discord.Embed(color=0x7289da)
                embed.title = f"You asked me to remind you about:" 
                embed.description = f'{themessagecontent}'
                embed.set_footer(text=f'Reminder ID: {ctx_}')
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
    bot.add_cog(reminders(bot))