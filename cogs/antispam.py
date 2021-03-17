import discord
from discord.ext import commands

mc0 = commands.CooldownMapping.from_cooldown(4.0, 2.5, commands.BucketType.user)
mc1 = commands.CooldownMapping.from_cooldown(4.0, 3.0, commands.BucketType.user)
mc2 = commands.CooldownMapping.from_cooldown(4.0, 4.0, commands.BucketType.user)
mc3 = commands.CooldownMapping.from_cooldown(4.0, 5.0, commands.BucketType.user)
mc4 = commands.CooldownMapping.from_cooldown(4.0, 6.0, commands.BucketType.user)

class AS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        pass
        # bucket = mc1.get_bucket(message)
        # retry_after = bucket.update_rate_limit()
        # if not message.author.bot:
        #     if retry_after:
        #         #check if antispam is enabled, if it is not, return
        #         await message.channel.send(f"Slow down! {message.author.mention}.", delete_after=2)
        #         def is_spammer(m):
        #             return m.author == message.author

        #         await message.channel.purge(limit=8, check=is_spammer) #goal would be for this to fire only once per incident so there isnt a ratelimit met
        #     else:
        #         return


def setup(bot):
    bot.add_cog(AS(bot))