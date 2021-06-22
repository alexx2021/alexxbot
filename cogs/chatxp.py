import asyncio
from utils.utils import on_level_up
import discord
from discord.ext import commands
from random import randint
import logging
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import bot_has_permissions, has_permissions
from discord.ext.buttons import Paginator
import aiohttp

logger = logging.getLogger('discord')

class Pag(Paginator):
    async def teardown(self):
        try:
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            #logger.warn(msg="HTTP Exception due to paginator in chatxpCog")
            pass

async def import_meesix(self, ctx):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f'https://mee6.xyz/api/plugins/levels/leaderboard/{ctx.guild.id}') as r: 
            data = await r.json()
            if r.status == 200:
                msg = await ctx.send('<a:loading:828842034630492231> Importing data from mee6...')
                if data["players"]:
                    users = data["players"]
                    async with self.bot.db.acquire() as connection:
                        for user in users:
                            userid = int(user["id"])
                            userxp = int(user["xp"])
                            await connection.execute('INSERT INTO xp VALUES ($1,$2,$3)', ctx.guild.id, userid, userxp)
                    await asyncio.sleep(1)
                    await msg.edit(content='<a:check:826577847023829032> Done importing data from mee6.')
                    return True
            else:
                await ctx.send('<a:x_:826577785173704754> There was an error fetching the data from mee6. Make sure that your server has existing mee6 level data before using this command.')
                return False
    

class levels(commands.Cog):
    """💬 Commands related to the chat leveling module"""
    def __init__(self, bot):
        self.bot = bot    
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 60, commands.BucketType.member
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.wait_until_ready()
        if message.author.bot:
            return
        if not message.guild:
            return
        ctx = await self.bot.get_context(message)
        if ctx.command:
            return
        
        try:
            enabled = self.bot.cache_lvlsenabled[message.guild.id]
            if 'TRUE' in enabled:
                pass
            else:
                return
        except KeyError:
            return

        try:
            if self.bot.cache_xpignoredchannels[ctx.guild.id][ctx.channel.id]:
                return
        except KeyError:
            pass

        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if not retry_after:
            async with self.bot.db.acquire() as connection:
                member = await connection.fetchrow('SELECT * FROM xp WHERE guild_id = $1 AND user_id = $2', message.guild.id, message.author.id)

                if member:
                    xp = member["user_xp"]
                    if xp == 1 or xp <= 1:
                        new_xp = xp + 1
                    elif xp < 30:
                        if xp >= 2:
                            new_xp = xp + randint(1, 2)
                    else:
                        new_xp = xp + randint(15, 25)
                     
                    await connection.execute('UPDATE xp SET user_xp = $1 WHERE guild_id = $2 AND user_id = $3', new_xp, message.guild.id, message.author.id)

                    level = (int (xp ** (1/3.25)))
                    new_level = (int (new_xp **(1/3.25)))
                    if new_level is not None and new_level > level:
                        await on_level_up(self, new_level, message)
                else:
                    await connection.execute('INSERT INTO xp VALUES($1,$2,$3)', message.guild.id, message.author.id, 1)
                # try:
                #     if member[1]:
                #         await connection.execute('DELETE FROM xp WHERE guild_id = ? AND user_id = ?', message.guild.id, message.author.id)
                #         await connection.execute('INSERT INTO xp VALUES($1,$2,$3)',(message.guild.id, message.author.id, member["user_xp"]))
                #         logger.warning(msg=f'Someones xp was doubled so I fixed it and set their xp to {member[0][2]} - user is {message.author} | userid {uid} | guildid {gid}')
                # except IndexError:
                #     pass
                
                #print('Got xp!')


    @commands.command(hidden=True)
    @commands.is_owner()
    async def testlvl(self, ctx):
        async with self.bot.db.acquire() as connection:
            guild = await connection.fetchrow("SELECT * FROM xp_enabled WHERE guild_id = $1", ctx.guild.id)
        if guild:
            if 'TRUE' in guild["enabled"]:
                perms = ctx.channel.permissions_for(ctx.guild.me)
                if perms.send_messages: #only send if we can
                    await ctx.channel.send(
                        f"Nice job {ctx.author.mention}, you leveled up to level **?**!")

    @commands.group(help='Use this to manage xp. (set, reset or import from mee6)')
    async def xp(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `set`, `reset`, `import`.')

    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @xp.command(help="Reset a member's XP and level.")
    @has_permissions(manage_guild=True)
    @bot_has_permissions(add_reactions=True)
    async def reset(self, ctx, member: discord.User = None):
        done = '<a:check:826577847023829032> Done. Reset your XP. '
        warn = discord.Embed(description = 'You are about to reset your own XP and rank. \nAre you sure?', color = discord.Color.red(), title = 'Warning')       
        error = '<a:x_:826577785173704754> This guild does not have xp enabled! There is nothing to reset!'
        try:
            enabled = self.bot.cache_lvlsenabled[ctx.guild.id]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send(error)
        except KeyError:
            return await ctx.send(error)           
        try:    
            if not member:
                msg = await ctx.send(embed = warn)
                await asyncio.sleep(0.25)
                await msg.add_reaction("✅")
                await asyncio.sleep(0.25)
                await msg.add_reaction("❌")
                reaction, person = await self.bot.wait_for(
                                "reaction_add",
                                timeout=60,
                                check=lambda reaction, user: user == ctx.author
                                and reaction.message.channel == ctx.channel)
                
                if str(reaction.emoji) == "✅":
                    async with self.bot.db.acquire() as connection:
                        await connection.execute('DELETE FROM xp WHERE guild_id = $1 AND user_id = $2', ctx.guild.id, ctx.author.id)
                    await ctx.send(done)
                else:
                    await ctx.send('Operation cancelled.')
            if member:
                done1 = f'<a:check:826577847023829032> Done. Reset the XP of {member.mention}.'
                warn2 = discord.Embed(description = f'You are about to reset {member.mention}\'s XP and rank.\nAre you sure?', color = discord.Color.red(), title = 'Warning') 
                
                msg = await ctx.send(embed = warn2)
                await asyncio.sleep(0.25)
                await msg.add_reaction("✅")
                await asyncio.sleep(0.25)
                await msg.add_reaction("❌")
                reaction, person = await self.bot.wait_for(
                                "reaction_add",
                                timeout=60,
                                check=lambda reaction, user: user == ctx.author
                                and reaction.message.channel == ctx.channel)
                
                if str(reaction.emoji) == "✅":
                    async with self.bot.db.acquire() as connection:
                        await connection.execute('DELETE FROM xp WHERE guild_id = $1 AND user_id = $2', ctx.guild.id, member.id)
                    await ctx.send(done1)
                else:
                    await ctx.send('Operation cancelled.')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send('You did not react in time.')
    
    @has_permissions(manage_guild=True)
    @commands.cooldown(3, 10, commands.BucketType.user)
    @xp.command(help='Sets a user\'s xp amount.')
    @commands.guild_only()
    async def set(self, ctx, member: discord.Member, xp: int):
        if xp >= 1000000000:
            return await ctx.send('https://tenor.com/view/cat-no-nope-breading-gif-7294729')
        if xp < 0:
            return await ctx.send('Value must not be less than 0.')

        async with self.bot.db.acquire() as connection:
            user = await connection.fetchrow('SELECT * FROM xp WHERE guild_id = $1 AND user_id = $2', ctx.guild.id, member.id) 
            if user:
                await connection.execute('UPDATE xp SET user_xp = $1 WHERE guild_id = $2 AND user_id = $3', xp, ctx.guild.id, member.id)
                await ctx.send(f'<a:check:826577847023829032> Updated {member.name}\'s XP! New value: **{xp}**.')
            else:
                await connection.execute('INSERT INTO xp VALUES($1,$2,$3)', ctx.guild.id, member.id, xp)
                await ctx.send(f'<a:check:826577847023829032> Set {member.name}\'s XP to **{xp}**!')

    @commands.max_concurrency(1, per=BucketType.guild, wait=False)
    @commands.cooldown(2, 15, commands.BucketType.guild)
    @has_permissions(manage_guild=True)
    @bot_has_permissions(add_reactions=True)
    @xp.command(help='Import your xp data directly from mee6!', name='import')
    async def importmee6(self, ctx):
        cmd = self.bot.get_command('levels toggle')
        warn = discord.Embed(description = 'You are about to reset the leveling system for this server.\n__ALL DATA WILL BE LOST__.\nAre you sure?', color = discord.Color.red(), title = 'Warning')
    
        try:
            enabled = self.bot.cache_lvlsenabled[ctx.guild.id]
            if 'TRUE' in enabled:
                msg = await ctx.send(embed = warn)
                await asyncio.sleep(0.25)
                await msg.add_reaction("✅")
                await asyncio.sleep(0.25)
                await msg.add_reaction("❌")
                reaction, person = await self.bot.wait_for(
                                "reaction_add",
                                timeout=60,
                                check=lambda reaction, user: user == ctx.author
                                and reaction.message.channel == ctx.channel)
                
                if str(reaction.emoji) == "✅":
                    async with self.bot.db.acquire() as connection:
                        await connection.execute('DELETE FROM xp WHERE guild_id = $1', ctx.guild.id)
                    if await import_meesix(self, ctx): #insert data here
                        pass
                else:
                    return await ctx.send('Operation cancelled.')

            else:
                if await import_meesix(self, ctx): #insert data here
                    await cmd.invoke(ctx) #enable

        except asyncio.exceptions.TimeoutError:
            return await ctx.send('You did not react in time.')
        except KeyError:
            if await import_meesix(self, ctx): #insert data here
                await cmd.invoke(ctx) #enable

    # @has_permissions(manage_guild=True)
    # @xp.command(help='Double xp in your server for a duration of your choice.')
    # async def double(self, ctx, hours:int=None):
    #     if hours is None:
    #         if self.bot.doublexp[ctx.guild.id] == False:
    #             return await ctx.send('<a:check:826577847023829032> Double XP is already disabled for this guild. Add a number (hours) as an argument to enable it. eg. `xp double 2`')
            
    #         self.bot.doublexp[ctx.guild.id] = False
    #         await ctx.send('<a:check:826577847023829032> Disabled double XP for this guild.')
    #     else:
    #         if self.bot.doublexp[ctx.guild.id] == True:
    #             return await ctx.send('<a:check:826577847023829032> Double XP is already enabled for this guild. Run the commands without a time argument to disable it. eg. `xp double`')

    #         if hours > 72:
    #             return await ctx.send('Duration cannot be longer than 72 hours.')
    #         self.bot.doublexp[ctx.guild.id] = True
    #         await ctx.send(f'<a:check:826577847023829032> Enabled double XP for this guild with a duration of `{hours}` hours.')
    #         realHours = hours * 3600
    #         await asyncio.sleep(realHours)
    #         self.bot.doublexp[ctx.guild.id] = False

    

    
    
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='Use this to check your chat level!')
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        error = '<a:x_:826577785173704754> This guild does not have xp enabled! Ask an admin to enable it with the `levels toggle` command!'
        try:
            enabled = self.bot.cache_lvlsenabled[ctx.guild.id]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send(error)
        except KeyError:
            return await ctx.send(error)            
        
        member = member or ctx.author
        if member.bot:
            return await ctx.send("<a:x_:826577785173704754> Bots don't have levels!")
        
        async with self.bot.db.acquire() as connection:
            db_member = await connection.fetchrow('SELECT * FROM xp WHERE guild_id = $1 AND user_id = $2', ctx.guild.id, member.id)
        
        
        if not db_member:
            embed = discord.Embed(
                title="<a:x_:826577785173704754> Error",
                description=f"{member.mention} hasn't sent a message yet. :(",
                colour=discord.Colour.red(),
            )
            return await ctx.send(embed=embed)
        
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetch('SELECT * FROM xp WHERE guild_id = $1 ORDER BY user_xp DESC', ctx.guild.id)

        rank = rows.index(db_member) + 1
        level = (int (db_member["user_xp"] ** (1/3.25)))
        db_member_xp = db_member["user_xp"]
        embed = discord.Embed(
            title=f"**Rank:** #{rank}",
            description=f"**Level: **{level}\n**Total XP:** {db_member_xp}\n**XP to next level:** {db_member_xp - round((level ** 3.25))} / {round(((level+ 1) ** 3.25) - (level ** 3.25))}",
            colour=discord.Colour.green(),
        )
        embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    #@commands.max_concurrency(1, per=BucketType.user, wait=False)
    @bot_has_permissions(add_reactions=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=("top","lb"), help = 'View the server leaderboard!')
    async def leaderboard(self, ctx: commands.Context):
            error = '<a:x_:826577785173704754> This guild does not have xp enabled! Ask an admin to enable it with the `levels toggle` command!'
            try:
                enabled = self.bot.cache_lvlsenabled[ctx.guild.id]
                if 'TRUE' in enabled:
                    pass
                else:
                    return await ctx.send(error)
            except KeyError:
                return await ctx.send(error)   
            
            async with self.bot.db.acquire() as connection:
                rankings = await connection.fetch('SELECT * FROM xp WHERE guild_id = $1 ORDER BY user_xp DESC', ctx.guild.id)

            if not rankings:
                embed = discord.Embed(
                title="<a:x_:826577785173704754> Error",
                description='There is no one to display on the leaderboard yet.\nTry again later!',
                colour=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)
            
            desc =[]
            for rank, record in enumerate(rankings, start=1):
                user_id = record["user_id"]
                user_xp = record["user_xp"]
                level = (int (record["user_xp"] ** (1/3.25)))

                e=f"**{rank}**. <@{user_id}> | {user_xp} XP, LVL {level}"
                desc.append(e)

            pager = Pag(
                title=f"Leaderboard for {ctx.guild}", 
                colour=discord.Colour.green(),
                timeout=15,
                entries=desc,
                length=10,
            )

            await pager.start(ctx)

    @bot_has_permissions(add_reactions=True)
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command(help='View the amount of XP you need for each level and more.',aliases=['ranks'])
    async def xpchart(self, ctx):
        lvls = []
        for i in range(150):
           lvls.append(f"Level: **{i}** \nTotal XP needed: {round(i ** 3.25)} \nXP needed to level up: {round(((i + 1) ** 3.25) - (i ** 3.25))}\n")
        pager = Pag(
            title=f"XP Leveling Chart", 
            colour=discord.Colour.blurple(),
            timeout=30,
            entries=lvls,
            length=10,
        )

        await pager.start(ctx)

    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpxp(self, ctx):
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM xp")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpxpe(self, ctx):
        async with self.bot.db.acquire() as connection:
            settings = await connection.fetch("SELECT * FROM xp_enabled")
        print('-----------dump-----------')
        print(settings)
        print('--------------------------')
        print(self.bot.cache_lvlsenabled)
        print('-----------dump-----------')

def setup(bot):
    bot.add_cog(levels(bot))