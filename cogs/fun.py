import discord
import random
import asyncio
import aiohttp
from discord.ext import commands
import random
import logging

from discord.ext.commands.cooldowns import BucketType

logger = logging.getLogger('discord')


#Fun Category
class fun(commands.Cog):
    """🙂 Fun commands"""
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(5.0, 10.0, commands.BucketType.user)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True

    @commands.guild_only() 
    @commands.command(help='Finds a random meme for you.')
    async def meme(self, ctx):
        # async with aiohttp.ClientSession() as session:
        #     async with session.get("https://meme-api.herokuapp.com/gimme") as response:
        #         data = await response.json()
        # embed = discord.Embed(title=data["title"], colour=0x7289da)
        # embed.set_image(url=data["url"])
        # embed.set_footer(
        #     text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url
        # )
        # await ctx.send(embed=embed)        
        
        
        async with aiohttp.ClientSession() as session:
            url = ['https://evergene.io/api/memes','https://evergene.io/api/dankmemes']
            async with session.get(random.choice(url)) as response:
                data = await response.json()
        embed = discord.Embed(title='Meme', colour=0x7289da)
        embed.set_image(url=data["url"])
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=embed)

    #fact command
    @commands.guild_only()
    @commands.command(help=('Finds a random fact for you.'))
    async def fact(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/fact') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Random Fact" 
                embed.description = (data['fact'])
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #rickrolls the person mentioned in dms
    @commands.guild_only()    
    @commands.command(help="Rickrolls the victim in their dms!",)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rickroll(self, ctx, user: discord.User):
        if ctx.guild.me.guild_permissions.manage_messages:
            await ctx.message.delete()
        if user.id == 247932598599417866:
        	await ctx.send(f'{ctx.author.mention} OOP! You cannot rickroll this user >:)', delete_after=3.0)
        else:
            try:
                await user.send('https://tenor.com/view/bumblebee-17029825')
                await user.send(f'a lovely surprise, courtesy of `{ctx.author}`')
                await ctx.send('👍')
            except:
                return
            finally:
        	    logger.info(msg=f'user rickrolled successfully by {ctx.author} ({ctx.author.id})')

    
    @commands.guild_only()
    @commands.command(help=('Hug someone.'))
    async def hug(self, ctx, member: discord.Member=None):
        if member is None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://nekos.life/api/v2/img/hug') as r: 
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = f"{ctx.author} hugged themselves!" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                    return
            
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/hug') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = f"{ctx.author} hugged {member} <3!" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(help=('Slap someone.'))
    async def slap(self, ctx, member: discord.Member=None):
        if member is None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://nekos.life/api/v2/img/slap') as r: 
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = f"{ctx.author} slapped themselves!" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                    return
            
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/slap') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = f"{ctx.author} slapped {member}!" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #chooses random result and tells you if you are gay :)
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.guild_only()
    @commands.command(help=('beep beep.'))
    async def gaydar(self, ctx, *, user):
        msg = await ctx.send('Beep Beep Beep....')
        await asyncio.sleep(1)
        await msg.edit(content='Results processed.')
        await asyncio.sleep(1)
        await msg.edit(content=f'{ctx.author.mention} Are you sure you want to know the truth? (say yes)')
        
        def check(m):
            return (m.content.lower() == 'yes') and (m.author.id == ctx.author.id)

        try:
            await self.bot.wait_for('message', check=check, timeout=15)
            isgaystring = ["They are confirmed ✨gay✨!!", "They are straight!","They are confirmed ✨gay✨!!", "They are straight!",
                "They are confirmed ✨gay✨!!", "They are straight!","Ask again later, im low on battery :(","eighwph49w-g-j-5hw-gjr"]
            await ctx.send(f'{random.choice(isgaystring)}')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'You did not decide in time, {ctx.author.mention}. ')

    #ask command from david's bot
    @commands.guild_only()
    @commands.command(aliases=["8ball"], help=('8ball.'))
    async def ask(self, ctx):
        list = ['As I see it, yes.', 'Ask again later.', 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.',
       'Don’t count on it.', 'It is certain.','It is decidedly so.','Most likely.','My reply is no.',' My sources say no.','Outlook not so good.',
       'Outlook good.','Reply hazy, try again.','Signs point to yes.','Very doubtful.','Without a doubt.','Yes.',' Yes – definitely.',' You may rely on it.']
        word = random.choice(list)
        await ctx.send("🎱 " + word)
    
    #cat command
    @commands.guild_only()
    @commands.command(help=('cat.'))
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/meow') as r:  #https://aws.random.cat/meow
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Kitty! 🐱" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #cat command
    @commands.guild_only()
    @commands.command(help=('dog.'))
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/woof') as r: #https://dog.ceo/api/breeds/image/random
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Doggo! 🐶" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #goose command 
    @commands.guild_only()
    @commands.command(help='goose.')
    async def goose(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/goose') as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = "Gooses ;)" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)

    #duck command
    @commands.guild_only()
    @commands.command(help=('duck.'))
    async def duck(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/v1/random?type=png') as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = "Duckies :3" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)

    #bunny command
    @commands.guild_only()
    @commands.command(help=('bunny.'))
    async def bunny(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.bunnies.io/v2/loop/random/?media=gif,png') as r:
                if r.status == 200:
                    data = await r.json()
        
                    picID = data['id']
                    picURL = f"https://bunnies.media/poster/{''.join(picID)}.png"

                    #was used for testing the command, turns out some gifs are too large to be displayed on discord
                    #await ctx.send(f'picID is {picID} and picURL is {picURL}')
                    
                    embed = discord.Embed(color=0x7289da)
                    embed.title = "Bunnies!" 
                    embed.set_image(url=(picURL))
                    embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)


    # #fun command from david's bot
    # @commands.command(help=('try it and see :)'))
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def fun(self, ctx, member: discord.Member):
    #     #await ctx.message.delete()
    #     await ctx.channel.purge(limit=1)
    #     user = await self.bot.fetch_user(ctx.author.id)
    #     await user.send("What's the password?")

    #     @self.bot.event
    #     async def on_message(message):
    #         await self.bot.process_commands(message)
    #         if message.author == self.bot.user:
    #             return
    #         if message.author == ctx.author:
    #             if not message.guild:
    #                 if message.content == '1234567890':
    #                     print(f"{message.author} got the password right (bee movie)")
    #                     await message.channel.send(':)')
    #                     victim = await self.bot.fetch_user(member.id)
    #                     file = "/home/container/pointlessfile.txt"
    #                     with open(file, 'r') as f:
    #                         for word in f:
    #                             await victim.send(word)
    #                             #await asyncio.sleep(0.5)
    #                 else:
    #                     await message.channel.send('incorrect password!!')

    @commands.command(help='Search urban dictionary for the given term.', aliases=['ud','urban'])
    @commands.guild_only()
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def urbandictionary(self, ctx, *msg):
        if len(msg) == 0:
            return await ctx.send('You need input a word in order for me to look it up!')
        word = ' '.join(msg)
        # Send request to the Urban Dictionary API and grab info
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'http://api.urbandictionary.com/v0/define?term={word}') as r:
                if r.status == 200:
                    data = await r.json()
                else:
                    return await ctx.send('<a:x_:826577785173704754> An error occurred. Please try again later.')
                embed = discord.Embed(description="No results found!", colour=0x7289da)

                #check if list has no length (no results)
                try:
                    if len(data["list"]) == 0:
                        return await ctx.send(embed=embed)
                except KeyError:
                    return await ctx.send('<a:x_:826577785173704754> An error occurred. Please try again later.')



        #check if fields are too large
        if (data["list"]):

            if (data["list"][0]['definition']):
                if len(data["list"][0]['definition']) > 1023:
                    embed1 = discord.Embed(description="Definition was too long to display.", colour=0x7289da)
                    return await ctx.send(embed=embed1)

            if (data["list"][0]['example']):
                if len(data["list"][0]['example']) > 1023:
                    embed2 = discord.Embed(description="Definition was too long to display.", colour=0x7289da)
                    return await ctx.send(embed=embed2)


        # Add results to the embed
        embed = discord.Embed(title="Word:", description=word, colour=embed.colour)
        embed.set_author(name='Urban Dictionary lookup')
        
        #apparently some queries only return one of these.
        if (data["list"][0]['definition']):
            embed.add_field(name="Top definition:", value=data['list'][0]['definition'])
        if (data["list"][0]['example']):
            embed.add_field(name="Examples:", value=data['list'][0]['example'])
        
        await ctx.send(embed=embed)
        

def setup(bot):
    bot.add_cog(fun(bot))