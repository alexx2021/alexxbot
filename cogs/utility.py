from io import BytesIO
import random
import discord
import datetime
from discord.ext.commands.core import bot_has_permissions, command, has_permissions
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import time
from utils.utils import get_or_fetch_member, getGuildIcon

def to_emoji(c):
    base = 0x1f1e6
    return chr(base + c)

#Utility Category
class utility(commands.Cog):
    """💡 A collection of utilities to make your life easier"""
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(5.0, 10.0, commands.BucketType.user)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True


    @commands.group(help='Commands to aid you in creating a poll.')
    async def poll(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `create`, `react`, `custom`.')

    @bot_has_permissions(add_reactions=True)
    @has_permissions(manage_messages=True)
    @commands.guild_only()
    @poll.command(help='Add reactions to the latest message in the channel it is used in.')
    async def react(self, ctx: commands.Context):
        count = 0
        async for msg in ctx.channel.history(limit=2):
            count += 1
            if count == 2:
                await msg.add_reaction('👍')
                await msg.add_reaction('👎')
                await ctx.send('<a:check:826577847023829032> Reactions added!', delete_after=2.0)
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            await ctx.message.delete()
    
    @bot_has_permissions(add_reactions=True)
    @has_permissions(manage_messages=True)
    @commands.guild_only()
    @poll.command(help='Create a poll!')
    async def create(self, ctx, *,question: str):
        e = discord.Embed(color = discord.Color.blurple(), title = 'Poll', description=question)
        e.set_footer(icon_url=ctx.author.display_avatar.url, text=f'Created by {ctx.author}')
        msg = await ctx.send(embed=e)
        await msg.add_reaction('👍')
        await msg.add_reaction('👎')
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            await ctx.message.delete()


    @bot_has_permissions(add_reactions=True)
    @poll.command(help='Enter a question and your preferred choices afterwards!')
    @commands.guild_only()
    async def custom(self, ctx, *question_and_choices: str):

        if len(question_and_choices) < 3:
            return await ctx.send('<a:x_:826577785173704754> Command is missing required arguments. Correct usage: `poll custom <question> <option1> <option2>....`')
        elif len(question_and_choices) > 21:
            return await ctx.send('You can only have up to 20 choices.')

        perms = ctx.channel.permissions_for(ctx.me)
        if not (perms.read_message_history or perms.add_reactions):
            return await ctx.send('I need Read Message History and Add Reactions permissions.')

        question = question_and_choices[0]
        choices = [(to_emoji(e), v) for e, v in enumerate(question_and_choices[1:])]

        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.manage_messages:
            await ctx.message.delete()

        body = "\n".join(f"{key}: {c}" for key, c in choices)

        e = discord.Embed(color = discord.Color.blurple(), title = 'Poll', description=f"{question}\n\n{body}")
        e.set_footer(icon_url=ctx.author.display_avatar.url, text=f'Created by {ctx.author}')
        poll = await ctx.send(embed=e)

        for emoji, _ in choices:
            await poll.add_reaction(emoji)

    #ping command
    @commands.command(help="🏓",)
    async def ping(self, ctx):
        await ctx.send(f'Pong! 🏓 {round(self.bot.latency*1000)}ms')
        # start = time.perf_counter()
        # end = time.perf_counter()
        # embed = discord.Embed(color = discord.Colour.random())
        # embed.title = "Pong! 🏓"
        # embed.description = (f'**Bot Latency:** {round(((end - start)*1000), 5)}ms\n**Websocket Latency:** {round(self.bot.latency*1000)}ms')
        # embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)
        # await ctx.send(embed=embed)

    #profile picture getter command
    @commands.guild_only()
    @commands.command(aliases=["avatar"], help=('Mention a user to get their profile picture link!'))
    async def pfp(self, ctx, *,  user : discord.User=None):
        if user is None:
            user = ctx.author
        ext = 'gif' if user.display_avatar.is_animated() else 'png'
        await ctx.send(file=discord.File(BytesIO(await user.display_avatar.read()), f"{user.id}.{ext}"))


    #userinfo command
    @commands.cooldown(3, 6, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=["whois"], help='Get information about a user.')
    async def userinfo(self, ctx, user: discord.User=None):
        if user is None:
            user = ctx.author
            roles = [role for role in user.roles]
            del roles[0]
            embed = discord.Embed(color=0x7289da, title=f"User Information")
            embed.set_author(name=f"{user}", icon_url=user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)

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
            embed.set_author(name=f"{user}", icon_url=user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)

            embed.add_field(name="ID:", value=user.id)
            embed.add_field(name="Joined Server On:", value=user.joined_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))

            embed.add_field(name="Created Account On:", value=user.created_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))
            embed.add_field(name="Display Name:", value=user.display_name)

            roles2 = [role.mention for role in roles]
            if roles2 == []:
                roles2 = ['None']
            if len(roles2) > 13:
                roles2 = ['Error. User has too many roles.']

            embed.add_field(name="Roles:", value="".join(roles2))
            embed.add_field(name="Highest Role:", value=user.top_role.mention)
            await ctx.send(embed=embed)
            return
        else:
            embed = discord.Embed(color=0x7289da, title=f"User Information")
            embed.set_author(name=f"{user} (not in this server)", icon_url=user.display_avatar.url)
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)

            embed.add_field(name="ID:", value=user.id)

            embed.add_field(name="Created Account On:", value=user.created_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))
            await ctx.send(embed=embed)


	#server info command
    @commands.command(help='Get information about this server.')
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="Server Information", colour=0x7289da, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=await getGuildIcon(self, ctx.guild))
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)
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


    @commands.guild_only()
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @commands.command(aliases=["embed",'embedcreator'], help='Creates an embed with your custom text.')
    async def embedmaker(self, ctx):
        
        perms = ctx.channel.permissions_for(ctx.guild.me)
        
        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            firstmessage = await ctx.send(f'{ctx.author.mention}, Send the title.')
            title = await self.bot.wait_for('message', check=check, timeout=30)
            if len(title.content) >= 256:
                return await ctx.send(f'<a:x_:826577785173704754> Title was **{len(title.content)}** chars long, but it cannot be longer than 256.')
            if perms.manage_messages:
                await firstmessage.delete()
        
            secondmessage = await ctx.send(f'{ctx.author.mention}, Send the description.')
            desc = await self.bot.wait_for('message', check=check, timeout=120)
            if perms.manage_messages:
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
    #                 embed.timestamp = discord.utils.utcnow()
    #                 embed.set_thumbnail(url=activity.album_cover_url)
    #                 embed.set_footer(text=f'Requested by {ctx.author}' + '\u200b')
    #                 await ctx.send(embed=embed)
    #                 await asyncio.sleep(1.5)


    #about command
    @commands.command(aliases=["info", "about"],help="Bot stats.")
    async def stats(self, ctx):
        delta_uptime = discord.utils.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = discord.Embed(color=0x7289da)
        embed.title = "About the Bot"
        embed.description = ('A multi-purpose discord bot written in python by `Alexx#7687` that is straightforward and easy to use. \nOh, and how could I forget? Cats. Lots of cats. 🐱')
        embed.add_field(name='Total servers', value=f' {len(self.bot.guilds)}', inline = True)
        embed.add_field(name='Total users', value = f'{len(set(self.bot.get_all_members()))}', inline = True)
        #embed.add_field(name='Ping', value=f'{round(self.bot.latency * 1000)}ms', inline = True)
        embed.add_field(name='Uptime', value=f"{days}d, {hours}h, {minutes}m, {seconds}s", inline=True)
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(hidden=True)
    async def invite(self, ctx):
        await ctx.reply('Thank you for your interest! :slight_smile: You can invite me with this link:\n<https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=2080763127&scope=bot>')
    
    @commands.command(hidden=True)
    async def support(self, ctx):
        await ctx.reply('Need help with the bot? Join here: https://discord.gg/zPWMRMXQ7H')

    


    @commands.group(help='Group of commands to manage giveaways.')
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `setup`, `reroll`.')

    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(add_reactions=True)
    @commands.cooldown(2, 10, commands.BucketType.guild) 
    @commands.guild_only()
    @giveaway.command(help='Create a giveaway! Delete it\'s respective message to cancel it!')
    async def setup(self,ctx):

        perms = ctx.channel.permissions_for(ctx.guild.me)

        def promptCheck(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            p1 = await ctx.send(f'{ctx.author.mention}, How long should this giveaway last?", `s|m|h|d` are acceptable time units.')
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

            if perms.manage_messages:
                await p1.delete()
            
            
            p2 = await ctx.send(f'{ctx.author.mention}, What will be given away?')
            description = await self.bot.wait_for('message', check=promptCheck, timeout=30)
            prize = description.content

            if len(prize) > 201:
                return await ctx.send(f'<a:x_:826577785173704754> Prize text cannot be longer than 200 chars.')
            
            if perms.manage_messages:
                await p2.delete()
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'Giveaway creation timed out.')

        e = f'`{prize}` will be given away in {counter}. \n**Is this correct?**'
        m = await ctx.send(e)
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
        if perms.manage_messages:
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

        async with self.bot.db.acquire() as connection:
            await connection.execute("INSERT INTO giveaways VALUES($1, $2, $3, $4, $5)", guild_id, channel_id, message_id, user_id, future)

    @has_permissions(manage_messages=True)
    @commands.cooldown(2, 10, commands.BucketType.guild) 
    @commands.guild_only()
    @giveaway.command(help='Rerolls to choose another winner.')
    async def reroll(self, ctx, msgID: discord.Message):
        users = None
        
        reactions = msgID.reactions
        for r in reactions:
            if r.emoji == "🎉":
                users = await r.users().flatten()
        if users == None:
            return await ctx.send('The message does not have "🎉" reacted to it.')


        try:
            users.pop(users.index(self.bot.user))
        except ValueError:
            pass

        if len(users) == 0:
            await ctx.send("No winner was decided")
        else:
            winner = random.choice(users)

            await ctx.send(f"**Congrats {winner.mention}!**\nPlease contact {msgID.author.mention} about your prize.")




def setup(bot):
    bot.add_cog(utility(bot))
