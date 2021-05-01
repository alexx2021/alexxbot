import contextlib
import io
import textwrap
from traceback import format_exception
import asyncio
from utils.utils import blacklist_user, unblacklist_user
import discord
import aiosqlite
import time
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
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

#Owner Category
class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        await ctx.send('👌')
        try:
            await self.bot.db.close()
            await self.bot.close()
        except Exception as e:
            await ctx.send(e)
    
    @commands.command()
    @commands.is_owner()
    async def sp(self, ctx):
        if self.bot.sp["enabled"] == False:
            self.bot.sp.update({"enabled": True})
            await ctx.send('True')
        else:
            self.bot.sp.update({"enabled": False})
            await ctx.send('False')

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()
        try:
            if self.bot.sp["enabled"] == True:
                print(f'{message.guild.name}({message.guild.id}) | {message.author}({message.author.id}) - {message.clean_content}')
        except KeyError:
            pass


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

        except Exception as e:
            await ctx.send(e)

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
    @commands.command()
    @commands.is_owner()
    async def rc(self, ctx, *, new_name):
        try:
            channel = ctx.message.channel
            await channel.edit(name=new_name)
            await ctx.send(f'Changed channel name to **{new_name}** ! ✅ ', delete_after=5.0)
        except Exception as e:
            await ctx.send(e)
    
    #deletes a channel
    @commands.command()
    @commands.is_owner()
    async def dc(self, ctx):
        try:
            await ctx.message.channel.delete()
        except Exception as e:
            await ctx.send(e)
    
    @commands.command()
    @commands.is_owner()
    async def cc(self, ctx,*, name):
        try:
            await ctx.guild.create_text_channel(name)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.is_owner()
    async def listperms(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.guild.me
        perm_list = ''
        for perm in member.guild_permissions:
            if perm[1] is False:
                perm_list += f'🔴 {perm[0]}\n'
            if perm[1] is True:
                perm_list += f'🟢 {perm[0]}\n'
            
        
        e = discord.Embed(description=f'**Permissions for {member}**\n\n{perm_list}', color = discord.Color.blurple())
            
        await ctx.send(embed = e)

    #bans a user
    @bot_has_permissions(ban_members=True)
    @commands.is_owner()    
    @commands.command()
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
    async def adduser(self, ctx, user: discord.User):
        if user.id == OWNER_ID:
            return await ctx.send('oops, you tried to blacklist yourself...')
        await blacklist_user(self, user)
        await ctx.send(f'{user} with the id of `{user.id}` was blacklisted ✅')

    @commands.command()
    @commands.is_owner()
    async def removeuser(self, ctx, user: discord.User):
        await unblacklist_user(self, user)
        await ctx.send(f'{user} with the id of `{user.id}` was removed from the blacklist ✅')

        
    @commands.command()
    @commands.is_owner()
    async def addguild(self, ctx, guild:int):
        async with self.bot.db.acquire() as c:
            await c.execute("INSERT INTO guildblacklist VALUES($1)", guild)
        await ctx.send(f'Guild with id of `{guild}` was blacklisted ✅')

    @commands.command()
    @commands.is_owner()
    async def removeguild(self, ctx, guild:int):
        async with self.bot.db.acquire() as c:
            await c.execute("DELETE FROM guildblacklist WHERE guild_id = $1", guild)
        await ctx.send(f'Guild with id of `{guild}` was removed from the blacklist ✅')

    @commands.command()
    @commands.is_owner()
    async def checkguild(self, ctx, guild:int):
        async with self.bot.db.acquire() as c:
            rows = await c.fetch("SELECT guild_id FROM guildblacklist WHERE guild_id = $1", guild)
            if not rows:
                return await ctx.send(f'Guild with id of `{guild}` was `NOT` found in the blacklist.')
            if rows:
                return await ctx.send(f'Guild with id of `{guild}` `was found` in the blacklist.')

    @commands.command()
    @commands.is_owner()
    async def whitelist(self, ctx, guild:int):
        async with self.bot.db.acquire() as c:
            await c.execute("INSERT INTO whitelist VALUES($1)", guild)
        self.bot.cache_whitelist.update({guild : True})
        await ctx.send(f'Guild with id of `{guild}` was whitelisted ✅')

    @commands.command()
    @commands.is_owner()
    async def unwhitelist(self, ctx, guild:int):
        async with self.bot.db.acquire() as c:
            await c.execute("DELETE FROM whitelist WHERE guild_id = $1", guild)
            self.bot.cache_whitelist.update({guild : False})
        await ctx.send(f'Guild with id of `{guild}` was removed from the whitelist ✅')


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
        
        start = time.perf_counter()

        try:
            with contextlib.redirect_stdout(stdout):
                exec(
                    f"async def func():\n{textwrap.indent(code, '    ')}", local_variables,
                )

                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except Exception as e:
            result = "".join(format_exception(e, e, e.__traceback__))
        
        end = time.perf_counter()

        pager = Pag(
            timeout=30,
            entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
            length=1,
            prefix="```py\n",
            suffix=f"```\n Time elapsed: {round(((end - start)*1000), 2)}ms"
        )

        await pager.start(ctx)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        def check(reaction, user):
            return str(reaction.emoji) == "🔁" and user == after.author and reaction.message == after
        
        if(before.author.bot):
            return
        if before.author == self.bot.user:
            return
        
        after_ctx = await self.bot.get_context(after)
        if (after.author.id == 247932598599417866):  
            if after_ctx.command:
                try:
                    await after.add_reaction("🔁")
                    reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=20)
                    try:
                        await after.clear_reaction(reaction.emoji)
                    except discord.HTTPException:
                        await asyncio.sleep(0.25)
                        await after.remove_reaction(reaction.emoji, self.bot.user)
                    await self.bot.process_commands(after)
                except asyncio.TimeoutError:
                    await after.remove_reaction("🔁", self.bot.user)

    
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



