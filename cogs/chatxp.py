import discord
from discord.ext import commands
from random import randint

from discord.utils import find

class ChatXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    
        self.cd_mapping = commands.CooldownMapping.from_cooldown(
            1, 60, commands.BucketType.member
        )

        self.leveling_dict = {
            range(0, 100): 0,
            range(100, 255): 1,
            range(255, 475): 2,
            range(475, 770): 3,
            range(770, 1550): 4,
            range(1550, 1625): 5,
            range(1625, 2205): 6,
            range(2205, 2900): 7,
            range(2205, 2900): 8, #?
            range(2900, 3465): 9,
            range(3465, 4000): 10,
            range(4000, 5775): 11,
            range(5775, 7030): 12,
            range(7030, 8450): 13,
            range(8450, 10045): 14,
            range(10045, 11825): 15, #?
            range(11825, 13800): 16,
            range(13800, 15980): 17,
            range(15980, 18375): 18,
            range(18375, 20995): 19,
            range(20995, 26950): 20,
            range(26950, 30305): 21,
            range(30305, 33925): 22,
            range(33925, 37820): 23,
            range(37820, 42000): 24,
            range(42000, 46475): 25,
            range(42000, 51255): 26,
            range(51255, 56350): 27,
            range(56350, 61770): 28,
            range(61770, 67525): 29,
            range(67525, 73625): 30,
            range(73625, 80080): 31,
            range(80080, 86900): 32,
            range(86900, 94095): 33,
            range(94095, 101675): 34,
            range(101675, 109650): 35,
            range(109650, 118030): 36,
            range(118030, 126825): 37,
            range(126825, 136045): 38,
            range(136045, 145700): 39,
            range(145700, 155800): 40,
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message): #add delete upon guild leave
        self.bot.wait_until_ready()
        if message.author.bot:
            return
        if not message.guild:
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
                new_xp = xp + randint(10, 25)

                level = find(lambda x: xp in x[0], self.leveling_dict.items())
                new_level = find(
                    lambda x: new_xp in x[0], self.leveling_dict.items()
                )
                if new_level[1] is not None and new_level[1] > level[1]:
                    self.bot.dispatch("level_up", new_level[1], message)
                
                query = 'UPDATE xp SET user_xp = ? WHERE guild_id = ? AND user_id = ?'
                params = (new_xp, gid, uid)
                await self.bot.xp.execute(query, params)
                await self.bot.xp.commit()
                print('bop')
            else:
                await self.bot.xp.execute('INSERT INTO xp VALUES(?,?,?)',(gid, uid, randint(10, 25)))
                await self.bot.xp.commit()
                print('boop')





    @commands.Cog.listener()
    async def on_level_up(self, level: int, message: discord.Message):
        guild = await self.bot.xp.execute_fetchall("SELECT * FROM lvlsenabled WHERE guild_id = ?",(message.guild.id,))
        if guild:
            if guild[1] == '1':
                perms = message.channel.permissions_for(message.guild.me)
                if perms.send_messages: #only send if we can
                    await message.channel.send(
                        f"Nice job {message.author.mention}, you leveled up to level {level}!")
        else:
            return

    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='Use this to check your chat level!')
    async def togglelevelmessages(self, ctx: commands.Context):
        guild = await self.bot.xp.execute_fetchall("SELECT * FROM lvlsenabled WHERE guild_id = ?",(ctx.guild.id,))
        if guild:
            if guild[1] == '1':
                pass
    
    @commands.cooldown(3, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.command(help='Use this to check your chat level!')
    async def rank(self, ctx: commands.Context, member: discord.Member = None):
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
                embed.set_footer(
                    text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url
                )
                return await ctx.send(embed=embed)
            
            query = 'SELECT * FROM xp WHERE guild_id = ? ORDER BY user_xp DESC' 
            params = (gid,)
            rows = await self.bot.xp.execute_fetchall(query, params)

            rank = rows.index(db_member[0]) + 1
            level = find(lambda x: db_member[0][2] in x[0], self.leveling_dict.items())
            embed = discord.Embed(
                title=f"{member.display_name}'s level",
                description=f"""**Rank:** {rank}\n**Level: **{level[1]}
                                            **XP: **{db_member[0][2] - level[0].start}/{level[0].stop - level[0].start} """,
                colour=discord.Colour.green(),
            )
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)



    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpxp(self, ctx):
        rows = await self.bot.xp.execute_fetchall("SELECT * FROM xp")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')

def setup(bot):
    bot.add_cog(ChatXP(bot))