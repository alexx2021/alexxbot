from io import BytesIO
import discord
import datetime
from discord.ext.commands.core import bot_has_permissions
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from time import perf_counter 
import time
# from discord import Spotify
# from discord import CustomActivity

#Utility Category
class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #ping command
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(help="Shows the latency of the bot in milliseconds.",)
    async def ping(self, ctx):
        start = time.perf_counter()
        end = time.perf_counter()
        embed = discord.Embed(color=0x7289da)
        embed.title = "Pong! 🏓"
        embed.description = (f'**Bot Latency:** {round(((end - start)*1000), 10)}ms\n**Websocket Latency:** {round(self.bot.latency*1000)}ms')
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
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
    @commands.guild_only()
    @commands.command(aliases=["whois"], help='Displays information about a mentioned user')
    async def userinfo(self, ctx, member: discord.Member=None):
        if member is None:
            member = ctx.author
        roles = [role for role in member.roles]
        del roles[0]
        embed = discord.Embed(color=0x7289da, title=f"User Information")
        embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)

        embed.add_field(name="ID:", value=member.id)
        embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))

        embed.add_field(name="Created Account On:", value=member.created_at.strftime("%a, %D %B %Y, %I:%M %p UTC"))
        embed.add_field(name="Display Name:", value=member.display_name)

        roles2 = [role.mention for role in roles]
        if roles2 == []:
            roles2 = ['None']
        if len(roles2) > 10:
            roles2 = ['Error. User has too many roles.']

        embed.add_field(name="Roles:", value="".join(roles2))
        embed.add_field(name="Highest Role:", value=member.top_role.mention)
        await ctx.send(embed=embed)

	#server info command
    @commands.cooldown(2, 5, commands.BucketType.user)
    @commands.command(help='Displays information about the server')
    async def serverinfo(self, ctx):
        embed = discord.Embed(title="Server Information", colour=0x7289da, timestamp=datetime.datetime.utcnow())
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
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
                return await ctx.send(f'Title was **{len(title.content)}** chars long, but it cannot be longer than 256.')
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
    #                 embed.set_footer(text=f'Requested by: {ctx.author}' + '\u200b')
    #                 await ctx.send(embed=embed)
    #                 await asyncio.sleep(1.5)



def setup(bot):
    bot.add_cog(Utility(bot))
