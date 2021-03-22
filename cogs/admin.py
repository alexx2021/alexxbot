import contextlib
import io
import textwrap
from traceback import format_exception
import asyncio
import discord
import aiosqlite
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions

BOT_ID = int(752585938630082641)
OWNER_ID = int(247932598599417866)

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content

from discord.ext.buttons import Paginator


class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

#Owner Category
class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    #gets current servers the bot is in
    @commands.command()
    @commands.is_owner()
    async def listguilds(self, ctx):
        servers = self.bot.guilds
        for guild in servers:
            embed = discord.Embed(colour=0x7289DA)
            embed.set_footer(text=f"Guild requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
            "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
            "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
            "\n" + "Created at " + str(guild.created_at), inline=False)
            embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})'))
            
            if guild.me.guild_permissions.administrator:
                admin = True
            else:
                admin = False

            embed.add_field(name='Permissions', value=f'Admin: {admin}') 
            embed.set_thumbnail(url=guild.icon_url)
            
            await ctx.send(embed=embed)
            await asyncio.sleep(1)

    #makes the bot leave the given server ID
    @commands.command()
    @commands.is_owner()
    async def leaveguild(self, ctx, serverid:int):
        try:
            await ctx.send(f'Left server with ID of `{serverid}` ✅')
            g = self.bot.get_guild(int(serverid))
            if not g:
                g = await self.bot.fetch_guild(int(serverid))
                await ctx.send('fetched guild')
            await g.leave()

        except:
            await ctx.send('An error occured.', delete_after=5.0)

    #owner only command to change the status of the bot
    @commands.command()
    @commands.is_owner()
    async def status(self, ctx,* ,status):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(f'{status}'))
        await ctx.send(f'Changed bot status to **{status}** ! ✅ ', delete_after=5.0)

    
    #simple say command to make the bot say something. Owner only atm
    @commands.command()
    @commands.is_owner()
    async def say(self, ctx,* ,args):
        mesg = ''.join(args)
        try:
            await ctx.message.delete()
        except discord.errors.Forbidden:
            pass
        return await ctx.send(mesg)
    
    #renames a channel
    @commands.command(hidden=True)
    @commands.is_owner()
    async def rc(self, ctx, *, new_name):
        try:
            channel = ctx.message.channel
            await channel.edit(name=new_name)
            await ctx.send(f'Changed channel name to **{new_name}** ! ✅ ', delete_after=5.0)
        except:
            await ctx.send('An error occured.', delete_after=5.0)
    
    #deletes a channel
    @commands.command(hidden=True)
    @commands.is_owner()
    async def dc(self, ctx):
        try:
            await ctx.message.channel.delete()
        except:
            await ctx.send('An error occured.', delete_after=5.0)
    
    @commands.command(hidden=True)
    @commands.is_owner()
    async def cc(self, ctx,*, name):
        try:
            await ctx.guild.create_text_channel(name)
        except:
            await ctx.send('An error occured.', delete_after=5.0)

    @commands.command()
    @commands.is_owner()
    async def listperms(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.message.author
        perm_list = [perm[0] for perm in member.guild_permissions if perm[1]]
        await ctx.send(perm_list)

    #bans a user
    @bot_has_permissions(ban_members=True)
    @commands.is_owner()    
    @commands.command(hidden=True)
    async def bean(self, ctx, user: discord.User,*, reason=None):
        if ctx.message.author.id == user.id: #checks to see if you are banning yourself
            return await ctx.send(f'{ctx.author.mention} you cannot ban yourself, silly human! `>.<`')
        if user.id == BOT_ID:
            return await ctx.send(f'{ctx.author.mention} you cannot ban me with my own commands! SMH.')

        try:
            await ctx.guild.ban(user, reason=f"By {ctx.author} for {reason}")
            await ctx.send(f'{user.mention} was banned! `>:(`')
        except:
            return await ctx.send("Could not ban this user.")


    # @commands.Cog.listener()
    # async def on_guild_join(self, guild):

    # has been moved to invitetracker to use the on_guild_join event there so the databases are only accessed once per join


    
    @commands.command()
    @commands.is_owner()
    async def adduser(self, ctx, user1: discord.User):
        userid = str(user1.id)
        if user1.id == OWNER_ID:
            return await ctx.send('oops, you tried to blacklist yourself...')

        async with aiosqlite.connect('blacklists.db') as c:    
            await c.execute("INSERT INTO userblacklist VALUES(?)", (userid,))
            await c.commit()
        await asyncio.sleep(0.25)
        
        
        users = await self.bot.bl.execute_fetchall("SELECT * FROM userblacklist")
        
        totalusers = []

        for user in users:
            totalusers.append(str(user[0]))
        
        self.bot.ubl.update({"users" : f"{totalusers}"})
        await ctx.send(f'User with id of `{user1.id}` was blacklisted ✅')

    @commands.command()
    @commands.is_owner()
    async def removeuser(self, ctx, user1: discord.User):
        userid = str(user1.id)
        async with aiosqlite.connect('blacklists.db') as c:
            await c.execute("DELETE FROM userblacklist WHERE user_id = ?",(userid,))
            await c.commit()
        await asyncio.sleep(0.25)
        
        users = await self.bot.bl.execute_fetchall("SELECT * FROM userblacklist")
        
        totalusers = []

        for user in users:
            totalusers.append(str(user[0]))
        
        self.bot.ubl.update({"users" : f"{totalusers}"})
        await ctx.send(f'User with id of `{user1.id}` was removed from the blacklist ✅')

    @commands.command()
    @commands.is_owner()
    async def checkuser(self, ctx, user: discord.User):
        async with aiosqlite.connect('blacklists.db') as c:
            rows = await c.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(user.id,),)
            if rows == []:
                return await ctx.send(f'User with id of `{user.id}` was `NOT` found in the blacklist.')
            if rows != []:
                return await ctx.send(f'User with id of `{user.id}` `was found` in the blacklist.')
        
    @commands.command()
    @commands.is_owner()
    async def addguild(self, ctx, guild:int):
        guildID = str(guild)
        async with aiosqlite.connect('blacklists.db') as c:
            await c.execute("INSERT INTO guildblacklist VALUES(?)", (guildID,))
            await c.commit()
        await ctx.send(f'Guild with id of `{guild}` was blacklisted ✅')

    @commands.command()
    @commands.is_owner()
    async def removeguild(self, ctx, guild:int):
        guildID = str(guild)
        async with aiosqlite.connect('blacklists.db') as c:
            await c.execute("DELETE FROM guildblacklist WHERE guild_id = ?",(guildID,))
            await c.commit()
        await ctx.send(f'Guild with id of `{guild}` was removed from the blacklist ✅')

    @commands.command()
    @commands.is_owner()
    async def checkguild(self, ctx, guild:int):
        guildID = str(guild)
        async with aiosqlite.connect('blacklists.db') as c:
            rows = await c.execute_fetchall("SELECT guild_id FROM guildblacklist WHERE guild_id = ?",(guildID,),)
            if rows == []:
                return await ctx.send(f'Guild with id of `{guild}` was `NOT` found in the blacklist.')
            if rows != []:
                return await ctx.send(f'Guild with id of `{guild}` `was found` in the blacklist.')




    @commands.command(name="eval")
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
        code = clean_code(code)

        local_variables = {
            "discord": discord,
            "commands": commands,
            "bot": self.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message
        }

        stdout = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))

        pager = Pag(
            timeout=100,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix="```"
        )

        await pager.start(ctx)



    
    # @commands.Cog.listener()
    # async def on_message_delete(self, message):
    #     snipe_message_author[message.channel.id] = message.author
    #     snipe_message_content[message.channel.id] = message.content
    #     await asyncio.sleep(120)
    #     try:
    #         del snipe_message_author[message.channel.id]
    #         del snipe_message_content[message.channel.id]
    #     except KeyError:
    #         #print('key error with pop in snipe command')
    #         pass

    # @commands.command(hidden=True)
    # @commands.is_owner()
    # async def snipe(self, ctx):
    #     channel = ctx.channel
    #     try:
    #         em = discord.Embed(title = f"Last deleted message in #{channel.name}", description = snipe_message_content[channel.id], color=0xffffff)
    #         em.set_footer(text = f"Message was sent by {snipe_message_author[channel.id]}")
    #         await ctx.send(embed = em)
    #     except KeyError:
    #         await ctx.send(f"There are no recently deleted messages in {channel.mention}")
    #         return

    # @commands.command(hidden=True)
    # @commands.is_owner()
    # async def dumpsnipe(self, ctx):
    #     await ctx.send(f'{snipe_message_content}')
    #     await ctx.send(f'{snipe_message_author}')

    # snipe_message_author = {}
    # snipe_message_content = {}


def setup(bot):
    bot.add_cog(Admin(bot))



