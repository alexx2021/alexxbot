
import discord
import asyncio
import datetime
import time
import random
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import bot_has_permissions, has_permissions

BOT_ID = int(752585938630082641)
TEST_BOT_ID = int(715446479837462548)

#Utility Category
class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_giveaways.start()

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.guild) 
    @commands.guild_only()
    @commands.command()
    async def giveaway(self,ctx): #check if giveaway already exists in the server
        def promptCheck(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            await ctx.send(f'{ctx.author.mention}, How long should this giveaway last?", `s|m|h|d` are acceptable time units.')
            timemsg = await self.bot.wait_for('message', check=promptCheck, timeout=30)
            
            timeinput = timemsg.content
            
            seconds = 0
            try: 
                if timeinput.lower().endswith("d"):
                    seconds += int(timeinput[:-1]) * 60 * 60 * 24
                    counter = f"{seconds // 60 // 60 // 24} day(s)"
                if timeinput.lower().endswith("h"):
                    seconds += int(timeinput[:-1]) * 60 * 60
                    counter = f"{seconds // 60 // 60} hour(s)"
                elif timeinput.lower().endswith("m"):
                    seconds += int(timeinput[:-1]) * 60
                    counter = f"{seconds // 60} minute(s)"
                elif timeinput.lower().endswith("s"):
                    seconds += int(timeinput[:-1])
                    counter = f"{seconds} second(s)"
                
                if seconds < 10:
                    await ctx.send(f"Time must not be less than 10 seconds.")
                    return
                if seconds > 7776000:
                    await ctx.send(f"Time must not be more than 90 days")
                    return
            except ValueError:
                return await ctx.send('Please check your time formatting and try again. s|m|h|d are valid time unit arguments.')

            
            
            await ctx.send(f'{ctx.author.mention}, What will be given away?')
            description = await self.bot.wait_for('message', check=promptCheck, timeout=30)
            prize = description.content

            if len(prize) > 1024:
                return await ctx.send(f'Prize text cannot be longer than 1024 chars.')

        
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'Giveaway creation timed out.')

        
        m = await ctx.send(f'❗\n`{prize}` will be given away in {counter}\n**Is this correct?**')
        try:
            await m.add_reaction("✅")
            await asyncio.sleep(0.25)
            await m.add_reaction("🇽")
        except discord.Forbidden:
            await ctx.send('I do not have permission to add reactions!')

        try:
            reaction, member = await self.bot.wait_for(
                "reaction_add",
                timeout=60,
                check=lambda reaction, user: user == ctx.author
                and reaction.message.channel == ctx.channel
            )
        except asyncio.exceptions.TimeoutError:
            await ctx.send("Confirmation Failure. Please try again.")
            return

        if str(reaction.emoji) not in ["✅", "🇽"] or str(reaction.emoji) == "🇽":
            await ctx.send("Cancelling giveaway!")
            return
        
        await asyncio.sleep(0.5)
        await m.delete()
        await asyncio.sleep(0.5)

        giveawayEmbed = discord.Embed(title="**Giveaway** 🥳 - react to enter!", description=prize, color=0x7289da)
        giveawayEmbed.set_footer(text=f"This giveaway ends {counter} from this message.")
        embedmsg = await ctx.send(embed=giveawayEmbed)
        await embedmsg.add_reaction("🎉")

        future = int(time.time()+seconds)
        guild_id = int(ctx.guild.id)
        message_id = int(embedmsg.id)
        user_id = int(ctx.author.id)
        channel_id = int(ctx.channel.id)

        await self.bot.rm.execute("INSERT INTO giveaways VALUES(?, ?, ?, ?, ?)", (guild_id, channel_id, message_id, user_id, future))
        await self.bot.rm.commit()

    
    
    
    
    
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
                guild = self.bot.get_guild(theguildID)
                guildchannel = guild.get_channel(thechannelid)
                message = await guildchannel.fetch_message(themessageid)
                
                users = await message.reactions[0].users().flatten()
                author = await self.bot.fetch_user(theuserid)
            except:
                TRID = f'{int(therowID)}'
                await self.bot.rm.execute("DELETE FROM giveaways WHERE OID = ?",(TRID,))
                await self.bot.rm.commit()
                return
            
            users.pop(users.index(bot))
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
    bot.add_cog(Giveaway(bot))