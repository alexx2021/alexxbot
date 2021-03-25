import discord
import aiohttp
from discord.ext import commands

#Fun Category
class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True)
    async def nsfwcommands(self, ctx):
        e = discord.Embed(Color=0, title = 'NSFW Commands',description='catgirl\nboobs\npussy\nspank\nhentai\nanal\nbj')
        await ctx.send(embed=e)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(aliases=['cg'],hidden=True)
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def catgirl(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/neko') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Catgirl" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(aliases=['boob'],hidden=True)
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def boobs(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/boobs') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Boobs" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True,aliases=['puss'])
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def pussy(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/pussy') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Pussy" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True)
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def spank(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/spank') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Spank" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True)
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def hentai(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/hentai') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Hentai" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True)
    async def trap(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/trap') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Trap" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)


    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True)
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def anal(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/anal') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "Anal" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.is_nsfw()
    @commands.command(hidden=True)
    @commands.cooldown(4, 10, commands.BucketType.channel)
    async def bj(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://nekos.life/api/v2/img/bj') as r: 
                data = await r.json()
                embed = discord.Embed(color=0x7289da)
                embed.title = "BJ" 
                try:
                    embed.set_image(url=(data['url']))
                except KeyError:
                    return await ctx.send('An error occurred, please try again later')
                embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
                await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(NSFW(bot))