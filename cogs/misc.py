import discord
import datetime
import asyncio
from discord import Activity, ActivityType
from discord.raw_models import RawMessageDeleteEvent
from utils.utils import check_if_important_msg, get_or_fetch_channel
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType


async def on_guild_join_bl_check(self, guild):
    god = guild.owner.id
    async with self.bot.db.acquire() as connection:
        rows = await connection.fetchrow("SELECT user_id FROM userblacklist WHERE user_id = $1", god) #checks if a user in BL owns the server
        if rows:
            await guild.leave()
            
            embed = discord.Embed(colour=0xe74c3c)
            embed.set_author(name=f"Left guild with blacklisted owner")
            embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
            "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
            "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
            "\n" + "Created at " + str(guild.created_at), inline=False)
            embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})')) 
            embed.set_thumbnail(url=guild.icon_url)
            
            chID = 813600852576829470
            ch = await get_or_fetch_channel(self, chID)
            await ch.send(embed=embed)
            
            return

    async with self.bot.db.acquire() as connection:
        rows = await connection.fetchrow("SELECT guild_id FROM guildblacklist WHERE guild_id = $1", guild.id)#checks if its a guild in the BL 
        if rows:
            await guild.leave()
            
            embed = discord.Embed(colour=0xe74c3c)
            embed.set_author(name=f"Left blacklisted guild")
            embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
            "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
            "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
            "\n" + "Created at " + str(guild.created_at), inline=False)
            embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})')) 
            embed.set_thumbnail(url=guild.icon_url)
            
            chID = 813600852576829470
            ch = await get_or_fetch_channel(self, chID)
            await ch.send(embed=embed)
            
            return


async def pop_all(self, guild):
    try:
        self.bot.cache_prefixes.pop(guild.id)
    except KeyError:
        pass
    
    try:
        self.bot.cache_whitelist.pop(guild.id)
    except KeyError:
        pass
    
    try:
        self.bot.cache_logs.pop(guild.id)
    except KeyError:
        pass
    
    try:
        self.bot.cache_autorole.pop(guild.id)
    except KeyError:
        pass
    
    try:
        self.bot.cache_welcome.pop(guild.id)
    except KeyError:
        pass

    try:
        self.bot.cache_lvlsenabled.pop(guild.id)
    except KeyError:
        pass

    try:
        self.bot.cache_lvlupmsg.pop(guild.id)
    except KeyError:
        pass

    try:
        self.bot.cache_xpignoredchannels.pop(guild.id)
    except KeyError:
        pass
    
    try:
        self.bot.cache_xproles.pop(guild.id)
    except KeyError:
        pass

    try:
        self.bot.cache_reactionroles.pop(guild.id)
    except KeyError:
        pass

    try:
        self.bot.cache_mediaonly.pop(guild.id)
    except KeyError:
        pass

class Events(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        # self.status_scroll.start()
        
    # @commands.Cog.listener()
    # async def on_guild_join(self, guild):
    #     try:
    #         await guild.text_channels[0].send(f"Hello {guild.name}! I am {self.bot.user.display_name}. Thank you for inviting me! \nThe available commands and the support server can be found with `_help`")
    #         await guild.text_channels[0].send('https://cdn.discordapp.com/attachments/386995303066107907/533479547589623810/unknown.png')
    #     except:
    #         return
    # @tasks.loop(minutes=1.0)
    # async def status_scroll(self):
    #     #await self.bot.change_presence(activity=Activity(name=f"{len(self.bot.guilds)} guilds" + " | _help ", type=ActivityType.watching))
    #     #await asyncio.sleep(60)
    #     await self.bot.change_presence(activity=discord.Streaming(name=f"_help | {len(self.bot.guilds)}s {len(self.bot.users)}u ", url='https://www.twitch.tv/alexxwastakenlol'))
    #     #await asyncio.sleep(60)


    # @status_scroll.before_loop
    # async def status_wait(self):
    #     await self.bot.wait_until_ready()



#################################################
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        embed = discord.Embed(colour=discord.Color.red(), title = 'Left a server :(')
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name=(str(guild.name)), value=str(guild.id),inline=False)
        embed.add_field(name='Server Owner', value=(f'{guild.owner}\n{guild.owner.id}'))
        embed.set_thumbnail(url=guild.icon_url)
        
        ch = await get_or_fetch_channel(self, 827244995576332288)
        if ch:
            await ch.send(embed=embed)  
        
        await asyncio.sleep(2)
        server = guild.id

        async with self.bot.db.acquire() as connection:
            await connection.execute("DELETE FROM prefixes WHERE guild_id = $1", server)

            await connection.execute("DELETE FROM pmuted_users WHERE guild_id = $1", server)

            await connection.execute("DELETE FROM welcome WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM autorole WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM logging WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM autogames WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM xp_ignoredchannels WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM xp_rewards WHERE guild_id = $1", server)

            await connection.execute("DELETE FROM reactionroles WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM mediaonly WHERE guild_id = $1", server)


            await connection.execute("DELETE FROM xp WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM xp_enabled WHERE guild_id = $1", server)
            await connection.execute("DELETE FROM xp_lvlup WHERE guild_id = $1", server)
        
        await pop_all(self, guild)


    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        embed = discord.Embed(colour=discord.Color.green(), title = 'New server!')
        embed.timestamp = datetime.datetime.utcnow()
        embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
        "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
        "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
        "\n" + "Created at " + str(guild.created_at), inline=False)
        embed.add_field(name='Server Owner', value=(f'{guild.owner}\n{guild.owner.id}'))
        embed.set_thumbnail(url=guild.icon_url)
        
        ch = await get_or_fetch_channel(self, 827244995576332288)
        if ch:
            await ch.send(embed=embed)
    
        await on_guild_join_bl_check(self, guild)
        
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            enabled = self.bot.cache_lvlsenabled[member.guild.id]
            if 'TRUE' in enabled:
                pass
            else:
                return
        except KeyError:
            return
        async with self.bot.db.acquire() as connection:
            await connection.execute('DELETE FROM xp WHERE guild_id = $1 AND user_id = $2', member.guild.id, member.id)


    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        if payload.guild_id:
            await check_if_important_msg(self, payload.guild_id, payload.message_id)
                


#################################################SHHHHHHHHHHH!
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @commands.cooldown(1, 5, commands.BucketType.channel)
    @commands.command()
    async def minty(self, ctx):

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            firstmessage = await ctx.send(f'{ctx.author.mention}, UWU! THIS IS A SECRET COMMAND! Enter anything to continue o.O')
            m1 = await self.bot.wait_for('message', check=check, timeout=30)
            
        
            secondmessage = await ctx.send(f'{ctx.author.mention}, Minty is a cool person and friend UWUWU, they are a big supporter of the bot and for that I say thank u! :) \n Minty club invite code: nnhu5yEh9x')
            thirdmessage = await ctx.send('To delete these messages, enter anything into chat again.')
            m2 = await self.bot.wait_for('message', check=check, timeout=120)
           
            

            await asyncio.sleep(1)
            await firstmessage.delete()
            await asyncio.sleep(1)
            await secondmessage.delete()
            await asyncio.sleep(1)
            await thirdmessage.delete()
            await asyncio.sleep(1)
            await ctx.message.delete()

        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'You did not reply in time :(')
    
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command()
    async def pong(self, ctx):
        await ctx.send(':thinking:')
    
    @commands.is_owner()
    @commands.command()
    async def test(self, ctx):
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if not perms.send_messages:
            return print('uh oh I cant speak!')
        if not perms.embed_links:
            await ctx.send('I am missing permisions to send embeds :(')
        


        
def setup(bot):
	bot.add_cog(Events(bot))
