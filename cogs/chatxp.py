import asyncio
import discord
from discord.ext import commands
from random import randint
from discord.ext.commands.cooldowns import BucketType
from discord.ext.commands.core import has_permissions
from discord.ext.buttons import Paginator

class Pag(Paginator):
    async def teardown(self):
        try:
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

#test
        
class ChatXP(commands.Cog):
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
        try:
            enabled = self.bot.arelvlsenabled[f"{message.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return
        except KeyError:
            return
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
                    new_xp = xp + randint(10, 25)

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





    @commands.Cog.listener()
    async def on_level_up(self, level: int, message: discord.Message):
        guild = await self.bot.xp.execute_fetchall("SELECT * FROM lvlsenabled WHERE guild_id = ?",(message.guild.id,))
        if guild:
            if guild[0][1] == 'TRUE':
                perms = message.channel.permissions_for(message.guild.me)
                if perms.send_messages: #only send if we can
                    await message.channel.send(
                        f"Nice job {message.author.mention}, you leveled up to level **{level}**!")

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

    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.command(help="Reset a member's XP and level.")
    @has_permissions(manage_guild=True)
    async def resetxp(self, ctx, member: discord.Member = None):
        done = discord.Embed(description = 'Done. Reset your XP. ', color = 0)
        done.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        warn = discord.Embed(description = 'You are about to reset your own XP and rank. \nAre you sure?', color = discord.Color.red(), title = 'Warning')       
        error = discord.Embed(description='This guild does not have xp enabled!\nThere is nothing to reset!', color = discord.Color.red(), title= ":x: Error")
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send(embed=error)
        except KeyError:
            return await ctx.send(embed=error)           
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
                    await ctx.send(embed = done)
                else:
                    await ctx.send('Operation cancelled.')
            if member:
                done1 = discord.Embed(description = f'Done. Reset the XP of {member.mention}.', color = 0)
                done1.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
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
                    await ctx.send(embed = done1)
                else:
                    await ctx.send('Operation cancelled.')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'You did not react in time.')

    
    
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='Use this to check your chat level!')
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
        error = discord.Embed(description='This guild does not have xp enabled!\nAsk an admin to enable it with the `togglechatleveling` command!', color = discord.Color.red(), title= ":x: Error")
        try:
            enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return await ctx.send(embed=error)
        except KeyError:
            return await ctx.send(embed=error)            
        
        member = member or ctx.author
        if member.bot:
            return await ctx.send("Bots don't have levels!")
        query = 'SELECT * FROM xp WHERE guild_id = ? AND user_id = ?' 
        gid = ctx.guild.id
        params = (gid, member.id)
        db_member = await self.bot.xp.execute_fetchall(query, params)
        
        
        if not db_member:
            embed = discord.Embed(
                title="Error :(",
                description=f"{member.mention} hasn't sent a message yet.",
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

    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(aliases=("top","lb"), help = 'View the server leaderboard!')
    async def leaderboard(self, ctx: commands.Context):
            error = discord.Embed(description='This guild does not have xp enabled!\nAsk an admin to enable it with the `togglechatleveling` command!', color = discord.Color.red(), title= ":x: Error")
            try:
                enabled = self.bot.arelvlsenabled[f"{ctx.guild.id}"]
                if 'TRUE' in enabled:
                    pass
                else:
                    return await ctx.send(embed=error)
            except KeyError:
                return await ctx.send(embed=error)   
            
            query = 'SELECT * FROM xp WHERE guild_id = ? ORDER BY user_xp DESC' 
            params = (ctx.guild.id,)
            rankings = await self.bot.xp.execute_fetchall(query, params)
            if not rankings:
                embed = discord.Embed(
                title="Error :(",
                description='There is no one to display on the leaderboard yet.\nTry again later!',
                colour=discord.Colour.red(),
                )
                return await ctx.send(embed=embed)
            
            desc =''
            for rank, record in enumerate(rankings, start=1):
                user_id = record[1]
                user_xp = record[2]
                level = (int (record[2] ** (1/3.25)))

                e=f"**{rank}**. <@{user_id}> | {user_xp} XP, LVL {level}\n"
                desc += e

            pager = Pag(
                title=f"Leaderboard for {ctx.guild}", 
                colour=discord.Colour.green(),
                timeout=20,
                entries=[desc[i: i + 2000] for i in range(0, len(desc), 2000)],
                length=1,
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
    bot.add_cog(ChatXP(bot))