from io import BytesIO
import discord
import datetime
from discord.ext.commands.core import bot_has_permissions, command, has_permissions
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import time
from utils.utils import get_or_fetch_member
# from discord import Spotify
# from discord import CustomActivity

#Utility Category
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #ping command
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(help="Shows the latency of the bot & websocket in milliseconds.",)
    async def ping(self, ctx):
        start = time.perf_counter()
        end = time.perf_counter()
        embed = discord.Embed(color = discord.Colour.random())
        embed.title = "Pong! 🏓"
        embed.description = (f'**Bot Latency:** {round(((end - start)*1000), 5)}ms\n**Websocket Latency:** {round(self.bot.latency*1000)}ms')
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    #profile picture getter command
    @commands.guild_only()
    @commands.command(aliases=["avatar"], help=('Mention a user to get their profile picture link!'))
    async def pfp(self, ctx, *,  user : discord.User=None):
        if user is None:
            user = ctx.author
        ext = 'gif' if user.is_avatar_animated() else 'png'
        await ctx.send(file=discord.File(BytesIO(await user.avatar_url.read()), f"{user.id}.{ext}"))


    #userinfo command
    @commands.cooldown(3, 6, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=["whois"], help='Displays information about a mentioned user.')
    async def userinfo(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author
            roles = [role for role in user.roles]
            del roles[0]
            embed = discord.Embed(color=0x7289da, title=f"User Information")
            embed.set_author(name=f"{user}", icon_url=user.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)

            embed.add_field(name="ID:", value=user.id)
            embed.add_field(name="Joined Server On:", value=user.joined_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))

            embed.add_field(name="Created Account On:", value=user.created_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))
            embed.add_field(name="Display Name:", value=user.display_name)

            roles2 = [role.mention for role in roles]
            if roles2 == []:
                roles2 = ['None']
            if len(roles2) > 10:
                roles2 = ['Error. User has too many roles.']

            embed.add_field(name="Roles:", value="".join(roles2))
            embed.add_field(name="Highest Role:", value=user.top_role.mention)
            await ctx.send(embed=embed)
            return
        
        member = await get_or_fetch_member(self, ctx.guild, user.id)
        if member:
            user = member
            roles = [role for role in user.roles]
            del roles[0]
            embed = discord.Embed(color=0x7289da, title=f"User Information")
            embed.set_author(name=f"{user}", icon_url=user.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)

            embed.add_field(name="ID:", value=user.id)
            embed.add_field(name="Joined Server On:", value=user.joined_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))

            embed.add_field(name="Created Account On:", value=user.created_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))
            embed.add_field(name="Display Name:", value=user.display_name)

            roles2 = [role.mention for role in roles]
            if roles2 == []:
                roles2 = ['None']
            if len(roles2) > 10:
                roles2 = ['Error. User has too many roles.']

            embed.add_field(name="Roles:", value="".join(roles2))
            embed.add_field(name="Highest Role:", value=user.top_role.mention)
            await ctx.send(embed=embed)
            return
        else:
            embed = discord.Embed(color=0x7289da, title=f"User Information")
            embed.set_author(name=f"{user} (not in this server)", icon_url=user.avatar_url)
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)

            embed.add_field(name="ID:", value=user.id)

            embed.add_field(name="Created Account On:", value=user.created_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))
            await ctx.send(embed=embed)


	#server info command
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.command(help='Displays information about the server.')
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="Server Information", colour=0x7289da, timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        # statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
        # # len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
        # # len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
        # # len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

        fields = [("ID", ctx.guild.id, True),
        ("Owner", ctx.guild.owner, True),
        ("Region", ctx.guild.region, True),
        ("Created at", ctx.guild.created_at.strftime("%m/%d/%Y %H:%M:%S"), True),
        ("Total members", len(ctx.guild.members), True),
        ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True)]
        #("\u200b", "\u200b", True)]

        # unused fields:
        #("Banned members", len(await ctx.guild.bans()), True),
        #("Invites", len(await ctx.guild.invites()), True),
        #("Statuses", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", True),


        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)


    @commands.cooldown(1, 4, commands.BucketType.user)
    @commands.guild_only()
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @bot_has_permissions(embed_links=True, manage_messages=True)
    @commands.command(aliases=["embed",'embedcreator'], help='Creates an embed with your custom text.')
    async def embedmaker(self, ctx):
    
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            firstmessage = await ctx.send(f'{ctx.author.mention}, Send the title.')
            title = await self.bot.wait_for('message', check=check, timeout=30)
            if len(title.content) >= 256:
                return await ctx.send(f'<a:x_:826577785173704754> Title was **{len(title.content)}** chars long, but it cannot be longer than 256.')
            await firstmessage.delete()
        
            secondmessage = await ctx.send(f'{ctx.author.mention}, Send the description.')
            desc = await self.bot.wait_for('message', check=check, timeout=120)
            await secondmessage.delete()


        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'Embed creation timed out.')

        embed = discord.Embed(title=title.content, description=desc.content, color=0)
        embed.set_footer(text=f'Created by {ctx.author}')
        await ctx.send(embed=embed)
    #
    # currently not in use
    #

    # @commands.command(help=('Gets list of users in your server listening to spotify, and what they are listening to.'))
    # @commands.guild_only()
    # @commands.cooldown(1, 10, commands.BucketType.guild)
    # async def getspotify(self, ctx):
    #     await ctx.send(f'Users in {ctx.guild.name} listening to spotify:')
    #     for user in ctx.guild.members:
    #         for activity in user.activities:
    #             if isinstance(activity, Spotify):
    #                 embed = discord.Embed(color=0x2ecc71)
    #                 embed.title = f"{user}"
    #                 embed.add_field(name="Song", value=activity.title)
    #                 embed.add_field(name="Artist", value=activity.artist)
    #                 embed.add_field(name="Album", value=activity.album)
    #                 embed.add_field(name="Track Link", value=f"[{activity.title}](https://open.spotify.com/track/{activity.track_id})")
    #                 embed.timestamp = datetime.datetime.utcnow()
    #                 embed.set_thumbnail(url=activity.album_cover_url)
    #                 embed.set_footer(text=f'Requested by {ctx.author}' + '\u200b')
    #                 await ctx.send(embed=embed)
    #                 await asyncio.sleep(1.5)


    #about command
    @commands.cooldown(2, 6, commands.BucketType.user)
    @commands.command(aliases=["info", "about"],help="Gives you information about the bot.")
    async def stats(self, ctx):
        embed = discord.Embed(color=0x7289da)
        embed.title = "About the Bot"
        embed.description = ('A multi-purpose discord bot written in python by `Alexx#7687` that is straightforward and easy to use. \nOh, and how could I forget? Cats. Lots of cats. 🐱')
        embed.add_field(name='Total servers', value=f' {len(self.bot.guilds)}', inline = True)
        embed.add_field(name='Total users', value = f'{len(set(self.bot.get_all_members()))}', inline = True)
        # embed.add_field(name='Ping', value=f'{round(self.bot.latency * 1000)}ms', inline = True)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.guild) 
    @commands.guild_only()
    @commands.command(help='Use this to create a giveaway in your server that randomly chooses the winner!')
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
                    await ctx.send(f"<a:x_:826577785173704754> Time must not be less than 10 seconds.")
                    return
                if seconds > 7776000:
                    await ctx.send(f"<a:x_:826577785173704754> Time must not be more than 90 days")
                    return
            except ValueError:
                return await ctx.send('<a:x_:826577785173704754> Please check your time formatting and try again. s|m|h|d are valid time unit arguments.')

            
            
            await ctx.send(f'{ctx.author.mention}, What will be given away?')
            description = await self.bot.wait_for('message', check=promptCheck, timeout=30)
            prize = description.content

            if len(prize) > 201:
                return await ctx.send(f'<a:x_:826577785173704754> Prize text cannot be longer than 200 chars.')

        
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'Giveaway creation timed out.')

        e = discord.Embed(color=0x7289da, title=f'`{prize}` will be given away in {counter}', description= '**Is this correct?**')
        m = await ctx.send(embed=e)
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

    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.command(help='Reminds you about something after the time you choose! \n __timeinput__: 1 second --> 1s, 1 minute --> 1m, 1 hour --> 1h, 1 day --> 1d \nChoose ONE time unit in the command.', aliases=["rm","remind"])
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
                await ctx.send(f"<a:x_:826577785173704754> Time must not be less than 10 seconds.")
                return
            if seconds > 7776000:
                await ctx.send(f"<a:x_:826577785173704754> Time must not be more than 90 days")
                return
            if len(text) > 1900:
                await ctx.send(f"<a:x_:826577785173704754> The text you provided is too long.")
                return
        except ValueError:
            return await ctx.send('<a:x_:826577785173704754> Please check your time formatting and try again. s|m|h|d are valid time unit arguments.')
        
        future = int(time.time()+seconds)
        id = int(ctx.author.id)
        remindtext = text
        #await ctx.send(f'{future-seconds} = now, {int(time.time()+seconds)} = future time, {remindtext} = content  ')

        rows3 = await self.bot.rm.execute_fetchall("SELECT OID, id, future, remindtext FROM reminders WHERE id = ?",(id,),)
        if rows3 != []:
            try:
                if rows3[2]:
                    return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention}, you cannot have more than 3 reminders at once!')
            except IndexError:
                pass

        await self.bot.rm.execute("INSERT INTO reminders VALUES(?, ?, ?)", (id, future, remindtext))
        await self.bot.rm.commit()
        

        e = discord.Embed(description=f"{ctx.author.mention}, I will remind you of `{text}` in {counter}.", color = 0x7289da)
        e.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=e)



def setup(bot):
    bot.add_cog(Utility(bot))
