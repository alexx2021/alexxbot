import asyncio
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
            logger.warn(msg="HTTP Exception due to paginator in lb")

async def import_meesix(self, ctx):
    async with aiohttp.ClientSession() as cs:
        async with cs.get(f'https://mee6.xyz/api/plugins/levels/leaderboard/{ctx.guild.id}') as r: 
            data = await r.json()
            if r.status == 200:
                msg = await ctx.send('<a:loading:828842034630492231> Importing data from mee6...')
                if data["players"]:
                    users = data["players"]
                    for user in users:
                        userid = user["id"]
                        userxp = user["xp"]
                        await self.bot.xp.execute('INSERT INTO XP VALUES (?,?,?)', (ctx.guild.id, userid, userxp,))
                    await self.bot.xp.commit()
                    await asyncio.sleep(0.5)
                    await msg.edit(content='<a:check:826577847023829032> Done importing data from mee6.')
                    return True
            else:
                await ctx.send('<a:x_:826577785173704754> There was an error fetching the data from mee6. Make sure that your server has existing mee6 level data before using this command.')
                return False
    
        
async def addRoles(self, message, level):
    if message.guild.me.guild_permissions.manage_roles:
        try:    
            r = self.bot.xproles[message.guild.id][level]
        except KeyError:
            return
        role = discord.utils.get(message.guild.roles, id= int(r))
        if role:
            if message.guild.me.top_role.position > role.position:
                await message.author.add_roles(role, reason=f"Role reward for level {level}.")

class Levels(commands.Cog):
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
            enabled = self.bot.arelvlsenabled[f"{message.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return
        except KeyError:
            return

        try:
            if self.bot.xpignoredchannels[ctx.guild.id][ctx.channel.id]:
                return
        except KeyError:
            pass

        bucket = self.cd_mapping.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if not retry_after:
            query = 'SELECT * FROM xp WHERE guild_id = ? AND user_id = ?' 
            gid = message.guild.id
            uid = message.author.id
            params = (gid, uid)
            member = await self.bot.xp.execute_fetchall(query, params)
            if member:
                xp = member[0][2]
                if xp == 0.5:
                    new_xp = xp + 0.5
                elif xp < 30:
                    if xp >= 1:
                        new_xp = xp + randint(1, 2)
                else:
                    new_xp = xp + randint(15, 25)

                level = (int (xp ** (1/3.25)))
                new_level = (int (new_xp **(1/3.25)))
                if new_level is not None and new_level > level:
                    self.bot.dispatch("level_up", new_level, message)
                
                query = 'UPDATE xp SET user_xp = ? WHERE guild_id = ? AND user_id = ?'
                params = (new_xp, gid, uid)
                await self.bot.xp.execute(query, params)
                await self.bot.xp.commit()
            else:
                await self.bot.xp.execute('INSERT INTO xp VALUES(?,?,?)',(gid, uid, 0.5))
                await self.bot.xp.commit()
            try:
                if member[1]:
                    query = 'DELETE FROM xp WHERE guild_id = ? AND user_id = ?' 
                    params = (gid, uid)
                    await self.bot.xp.execute_fetchall(query, params)
                    await self.bot.xp.execute('INSERT INTO xp VALUES(?,?,?)',(gid, uid, member[0][2]))
                    await self.bot.xp.commit()
                    logger.warning(msg=f'Someones xp was doubled so I fixed it and set their xp to {member[0][2]} - user is {message.author} | userid {uid} | guildid {gid}')
            except IndexError:
                pass
            
            #print('Got xp!')





    @commands.Cog.listener()
    async def on_level_up(self, level: int, message: discord.Message):
        try:
            if 'TRUE' in self.bot.arelvlmsg[message.guild.id]:
               await addRoles(self, message, level)
            else:
                return await addRoles(self, message, level)
        except KeyError:
            return await addRoles(self, message, level)
        
        perms = message.channel.permissions_for(message.guild.me)
        if perms.send_messages: #only send if we can
            await message.channel.send(
                f"Nice job {message.author.mention}, you are now level **{level}**!")


    @commands.command(hidden=True)
    @commands.is_owner()
    async def testlvl(self, ctx):
        guild = await self.bot.xp.execute_fetchall("SELECT * FROM lvlsenabled WHERE guild_id = ?",(ctx.guild.id,))
        if guild:
            if guild[0][1] == 'TRUE':
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
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
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
                    query = 'DELETE FROM xp WHERE guild_id = ? AND user_id = ?' 
                    gid = ctx.guild.id
                    uid = ctx.author.id
                    params = (gid, uid)
                    await self.bot.xp.execute_fetchall(query, params)
                    await self.bot.xp.commit()
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
                    query = 'DELETE FROM xp WHERE guild_id = ? AND user_id = ?' 
                    gid = ctx.guild.id
                    uid = member.id
                    params = (gid, uid)
                    await self.bot.xp.execute_fetchall(query, params)
                    await self.bot.xp.commit()
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

        query = 'SELECT * FROM xp WHERE guild_id = ? AND user_id = ?' 
        gid = ctx.guild.id
        uid = member.id
        params = (gid, uid)
        user = await self.bot.xp.execute_fetchall(query, params)
        if user:
            query = 'UPDATE xp SET user_xp = ? WHERE guild_id = ? AND user_id = ?'
            params = (xp, gid, uid)
            await self.bot.xp.execute(query, params)
            await self.bot.xp.commit()
            await ctx.send(f'<a:check:826577847023829032> Updated {member.name}\'s XP! New value: **{xp}**.')
        else:
            await self.bot.xp.execute('INSERT INTO xp VALUES(?,?,?)',(gid, uid, xp))
            await self.bot.xp.commit()
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
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
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
                    query = 'DELETE FROM xp WHERE guild_id = ?' 
                    gid = ctx.guild.id
                    params = (gid,)
                    await self.bot.xp.execute(query, params)
                    await self.bot.xp.commit() # xp is still enabled no need to disable first
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

    
    
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='Use this to check your chat level!')
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        error = '<a:x_:826577785173704754> This guild does not have xp enabled! Ask an admin to enable it with the `levels toggle` command!'
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send(error)
        except KeyError:
            return await ctx.send(error)            
        
        member = member or ctx.author
        if member.bot:
            return await ctx.send("<a:x_:826577785173704754> Bots don't have levels!")
        query = 'SELECT * FROM xp WHERE guild_id = ? AND user_id = ?' 
        gid = ctx.guild.id
        params = (gid, member.id)
        db_member = await self.bot.xp.execute_fetchall(query, params)
        
        
        if not db_member:
            embed = discord.Embed(
                title="<a:x_:826577785173704754> Error",
                description=f"{member.mention} hasn't sent a message yet. :(",
                colour=discord.Colour.red(),
            )
            return await ctx.send(embed=embed)
        
        query = 'SELECT * FROM xp WHERE guild_id = ? ORDER BY user_xp DESC' 
        params = (gid,)
        rows = await self.bot.xp.execute_fetchall(query, params)

        rank = rows.index(db_member[0]) + 1
        level = (int (db_member[0][2] ** (1/3.25)))
        embed = discord.Embed(
            title=f"**Rank:** #{rank}",
            description=f"**Level: **{level}\n**Total XP:** {db_member[0][2]}\n**XP to next level:** {db_member[0][2] - round((level ** 3.25))} / {round(((level+ 1) ** 3.25) - (level ** 3.25))}",
            colour=discord.Colour.green(),
        )
        embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    #@commands.max_concurrency(1, per=BucketType.user, wait=False)
    @bot_has_permissions(add_reactions=True, manage_messages=True)
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=("top","lb"), help = 'View the server leaderboard!')
    async def leaderboard(self, ctx: commands.Context):
            error = '<a:x_:826577785173704754> This guild does not have xp enabled! Ask an admin to enable it with the `levels toggle` command!'
            try:
                enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
                if 'TRUE' in enabled:
                    pass
                else:
                    return await ctx.send(error)
            except KeyError:
                return await ctx.send(error)   
            
            query = 'SELECT * FROM xp WHERE guild_id = ? ORDER BY user_xp DESC' 
            params = (ctx.guild.id,)
            rankings = await self.bot.xp.execute_fetchall(query, params)
            if not rankings:
                embed = discord.Embed(
                title="<a:x_:826577785173704754> Error",
                description='There is no one to display on the leaderboard yet.\nTry again later!',
                colour=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)
            
            desc =[]
            for rank, record in enumerate(rankings, start=1):
                user_id = record[1]
                user_xp = record[2]
                level = (int (record[2] ** (1/3.25)))

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

    @bot_has_permissions(add_reactions=True, manage_messages=True)
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
        rows = await self.bot.xp.execute_fetchall("SELECT * FROM xp")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpxpe(self, ctx):
        settings = await self.bot.xp.execute_fetchall("SELECT * FROM chatlvlsenabled")
        print('-----------dump-----------')
        print(settings)
        print('--------------------------')
        print(self.bot.arelvlsenabled)
        print('-----------dump-----------')

def setup(bot):
    bot.add_cog(Levels(bot))