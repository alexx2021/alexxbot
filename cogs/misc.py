import discord
import asyncio
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType




class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            await guild.text_channels[0].send(f"Hello {guild.name}! I am {self.bot.user.display_name}. Thank you for inviting me! \nThe available commands and the support server can be found with `_help`")
            await guild.text_channels[0].send('https://cdn.discordapp.com/attachments/386995303066107907/533479547589623810/unknown.png')
        except:
            return


#################################################
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await asyncio.sleep(2)
        server = guild.id


        await self.bot.sc.execute("DELETE FROM logging WHERE server_id = ?",(server,))
        await self.bot.sc.commit()

        await asyncio.sleep(1)
        await self.bot.pr.execute("DELETE FROM prefixes WHERE guild_id = ?",(server,))
        await self.bot.pr.commit()

        await asyncio.sleep(1)
        await self.bot.m.execute("DELETE FROM pmuted_users WHERE guild_id = ?",(server,))
        await self.bot.m.commit()

        await asyncio.sleep(1)
        await self.bot.sc.execute("DELETE FROM welcome WHERE server_id = ?",(server,))
        await self.bot.sc.commit()

        await asyncio.sleep(1)
        await self.bot.sc.execute("DELETE FROM autorole WHERE guild_id = ?",(server,))
        await self.bot.sc.commit()

#################################################SHHHHHHHHHHH!
    @commands.max_concurrency(1, per=BucketType.channel, wait=False)
    @commands.cooldown(1, 3, commands.BucketType.channel)
    @commands.command(hidden=True)
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
    @commands.command(hidden=True)
    async def pong(self, ctx):
        await ctx.send(':thinking:')


    
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
