import discord
import random
import asyncio
import aiohttp
from discord.ext import commands
import random


#Fun Category
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #rickrolls the person mentioned in dms
    @commands.guild_only()    
    @commands.command(help="Rickrolls the victim in their dms!",)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rickroll(self, ctx, user: discord.User):
        await ctx.message.delete()
        if user.id == 247932598599417866:
        	await ctx.send(f'{ctx.author.mention} OOP! You cannot rickroll this user >:)', delete_after=3.0)
        else:
            try:
                await user.send('https://tenor.com/view/bumblebee-17029825')
                await user.send(f'a lovely surprise, courtesy of `{ctx.author}`')
            except:
                return
            finally:
        	    print(f'user rickrolled successfully by {ctx.author}')

    #sends a cat to the person mentioned in dms  
    # 
    # currently disabled
    #   
    # @commands.command(help="sends cats to someone in their dms!",) 
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def sendcat(self, ctx, user: discord.User):
    #     user = await self.bot.fetch_user(user.id)
    #     await ctx.message.delete()

    #     response = requests.get('https://aws.random.cat/meow') 
    #     data = response.json()
    #     embed = discord.Embed(color=0x0000ff)
    #     embed.title = "cats 4 u... sent with love :3" 
    #     embed.set_image(url=(data['file']))
    #     embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
    #     await user.send(embed=embed)
    
    
    # #hugs
    # @commands.guild_only()
    # @commands.command(help=('Hug another user!'))
    # async def hug(self, ctx, user: discord.User):
    #     hugstring = ["https://i.imgur.com/OgcCCPE.gifv","https://tenor.com/view/hug-love-hi-bye-cat-gif-15999080","https://tenor.com/view/milk-and-mocha-hug-love-heart-couple-gif-17258498","https://tenor.com/view/virtual-hug-penguin-love-heart-gif-14712845","https://tenor.com/view/cat-cuddling-kitty-kittens-hug-gif-17782164","https://tenor.com/view/kitten-cuddle-cat-cats-hug-gif-12568441","https://tenor.com/view/hugs-cats-hug-me-come-here-gif-13347201"]
    #     await ctx.send(f'**{ctx.author} hugged {user} :3**') 
    #     await ctx.send(f'{random.choice(hugstring)}') 
    
    #fact command
    @commands.guild_only()
    @commands.command(help=('Spits out a random fact!'))
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def fact(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/fact') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Random Fact" 
                embed.description = (data['fact'])
                embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)
    
    @commands.guild_only()
    @commands.command(help=('Hug someone.'))
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def hug(self, ctx, member: discord.Member=None):
        if member is None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://nekos.life/api/v2/img/hug') as r: 
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = f"{ctx.author} hugged themselves!" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                    return
            
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/hug') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = f"{ctx.author} hugged {member} <3!" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.command(help=('Slap someone.'))
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def slap(self, ctx, member: discord.Member=None):
        if member is None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://nekos.life/api/v2/img/slap') as r: 
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = f"{ctx.author} slapped themselves!" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                    return
            
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/slap') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = f"{ctx.author} slapped {member}!" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #chooses random result and tells you if you are gay :)
    @commands.guild_only()
    @commands.command(help=('beep beep'))
    async def gaydar(self, ctx, *, user):
        await ctx.send('Beep Beep Beep....')
        await asyncio.sleep(0.5)
        await ctx.send('Results processed.')
        await asyncio.sleep(0.5)
        await ctx.send(f'{ctx.author.mention} Are you sure you want to know the truth? (say yes)')
        
        def check(m):
            return m.content == 'yes'

        try:
            await self.bot.wait_for('message', check=check, timeout=10)
            isgaystring = ["They are confirmed ✨gay✨!!", "They are straight!","Ask again later, im low on battery :(","eighwph49w-g-j-5hw-gjr"]
            await ctx.send(f'{random.choice(isgaystring)}')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'You did not decide in time, {ctx.author.mention}. ')

    #ask command from david's bot
    @commands.guild_only()
    @commands.command(aliases=["8ball"], help=('8ball but better'))
    async def ask(self, ctx):
        list = ['no', 'yes', 'idk', 'not sure', 'possibly']
        word = random.choice(list)
        await ctx.send(word)
    
    #cat command
    @commands.guild_only()
    @commands.command(help=('cat.'))
    @commands.cooldown(5, 10, commands.BucketType.channel)
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/meow') as r:  #https://aws.random.cat/meow
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Catz" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #cat command
    @commands.guild_only()
    @commands.command(help=('dog.'))
    @commands.cooldown(5, 10, commands.BucketType.channel)
    async def dog(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/woof') as r: #https://dog.ceo/api/breeds/image/random
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Dogz" 
                embed.set_image(url=(data['url']))
                embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    #goose command 
    @commands.guild_only()
    @commands.command(help='goose.')
    @commands.cooldown(5, 10, commands.BucketType.channel)
    async def goose(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/goose') as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = "Gooses ;)" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)

    #duck command
    @commands.guild_only()
    @commands.command(help=('duck.'))
    @commands.cooldown(5, 10, commands.BucketType.channel)
    async def duck(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://random-d.uk/api/v1/random?type=png') as r:
                if r.status == 200:
                    data = await r.json()
                    embed = discord.Embed(color=0x7289da)
                    embed.title = "Duckz" 
                    embed.set_image(url=(data['url']))
                    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
                    await ctx.send(embed=embed)

    #bunny command
    @commands.guild_only()
    @commands.command(help=('bunny.'))
    @commands.cooldown(5, 10, commands.BucketType.channel)
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
                    embed.title = "Bunnyz" 
                    embed.set_image(url=(picURL))
                    embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
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
            return await ctx.send('You need to have a word in there to look it up!')
        word = ' '.join(msg)
        # Send request to the Urban Dictionary API and grab info
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'http://api.urbandictionary.com/v0/define?term={word}') as r:
                if r.status == 200:
                    data = await r.json()
                else:
                    return await ctx.send('An error occurred. Please try again later.')
                embed = discord.Embed(description="No results found!", colour=0x7289da)

                #check if list has no length (no results)
                try:
                    if len(data["list"]) == 0:
                        return await ctx.send(embed=embed)
                except KeyError:
                    return await ctx.send('An error occurred. Please try again later.')



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
    bot.add_cog(Fun(bot))