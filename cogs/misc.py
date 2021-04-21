import discord
import datetime
import asyncio
from discord import Activity, ActivityType
from utils.utils import get_or_fetch_channel
from discord.ext import commands, tasks
from discord.ext.commands.cooldowns import BucketType




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


        await asyncio.sleep(0.25)
        await self.bot.pr.execute("DELETE FROM prefixes WHERE guild_id = ?",(server,))
        await self.bot.pr.commit()

        await asyncio.sleep(0.25)
        await self.bot.m.execute("DELETE FROM pmuted_users WHERE guild_id = ?",(server,))
        await self.bot.m.commit()

        await asyncio.sleep(0.25)
        await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
        await self.bot.sc.execute("DELETE FROM autorole WHERE guild_id = ?",(server,))
        await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server,))
        await self.bot.sc.execute("DELETE FROM autogames WHERE guild_id = ?",(server,))
        await self.bot.sc.execute("DELETE FROM ignoredchannels WHERE guild_id = ?",(server,))
        await self.bot.sc.execute("DELETE FROM levelrewards WHERE guild_id = ?",(server,))
        await self.bot.sc.commit()

        await asyncio.sleep(0.25)
        await self.bot.xp.execute("DELETE FROM xp WHERE guild_id = ?",(server,))
        await self.bot.xp.execute("DELETE FROM lvlsenabled WHERE guild_id = ?",(server,))
        await self.bot.xp.execute("DELETE FROM chatlvlsenabled WHERE guild_id = ?",(server,))
        await self.bot.xp.commit()

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

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        try:
            enabled = self.bot.arelvlsenabled[f"{member.guild.id}"]
            if 'TRUE' in enabled:
                pass
            else:
                return
        except KeyError:
            return

        query = 'DELETE FROM xp WHERE guild_id = ? AND user_id = ?' 
        gid = member.guild.id
        uid = member.id
        params = (gid, uid)
        await self.bot.xp.execute_fetchall(query, params)
        await self.bot.xp.commit()

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
            return print('good')
        if not perms.embed_links:
            await ctx.send('I am missing permisions to send embeds :(')
        

    
    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     #await self.bot.process_commands(message)
    #     message.content = message.content.lower()
    #     if message.author == self.bot.user:
    #         return

        # #checks if the channel is blacklisted for on_message reactions/functions
        # if message.channel.id in [741054231661903907, 778760950836494336]:
        #     return

        # if 'alex' in message.content:
            
        #     user = self.bot.get_user(247932598599417866)

        #     if not message.guild:
        #         await user.send(f'`{message.author}` mentioned you in dms with the bot! \n [{message.content}]')

        #     else:
        #         embed = discord.Embed(color=0x7289da)
        #         embed.set_author(name=f"{message.author}", icon_url=message.author.avatar_url)
        #         embed.title = f"You were mentioned in #{message.channel.name}" 
        #         embed.description = f'{message.content}'
        #         embed.add_field(name='Message link', value=f'[Click here]({message.jump_url})')
        #         embed.timestamp = datetime.datetime.utcnow()
        #         embed.set_footer(text=f'guild = {message.guild.name}'+ '\u200b')
        #         await user.send(embed=embed)

        # if 'smacc' in message.content:
        #     try:
        #         await message.add_reaction('<:smacc:778433548909674497>') 
        #     except:
        #         return

        # if ':(' in message.content:
        #     try:
        #         await message.add_reaction('😦') 
        #     except:
        #         return
       
        # if 'hmm' in message.content:
        #     try:
        #         await message.add_reaction('<:ThinkEyes:411392266851057675>')  
        #     except:
        #         return
        
def setup(bot):
	bot.add_cog(Events(bot))
