import asyncio
import discord
from discord.ext import commands
from random import randint, shuffle
import random
import time


async def scramble_word():
    words = ['hello', 'goodbye', 'discord', 'alex','boost',
    'online','offline', 'nitro', 'bot', 'server','program',
    'python',
    ]
    word = random.choice(words)
    unscram = word
    word = list(word)
    shuffle(word)
    scram = ''.join(word)
    returnList = [scram, unscram]
    return returnList

async def check_word(self, ctx, data, counter):
    try:    
        def check(message):
            return message.channel == ctx.channel
        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if data[1] in msg.content:
            pointCount = randint(1,3)
            return await ctx.send(f'{msg.author.mention} got the word correct first, and they got {pointCount} points!')
        else:
            counter += 1 
            if counter > 20:
                return await ctx.send('No one got the correct answer in time :(')
            else:
                print(counter)
                await check_word(self, ctx, data, counter)
    except asyncio.exceptions.TimeoutError:
        return await ctx.send('No one replied in time :(')


async def send_word(self, ctx):
    data = self.bot.chatgames[ctx.guild.id]
    data.update({"lastrun": time.time()})


    incorrectCounter = 0
    titles = ['❗  Unscramble Event!', '🤔  Unscramble the word!','🥺  Pls unscramble!' ]
    data = await scramble_word()
    
    underscores = ""
    counter = 0
    length = len(list(data[0]))
    for letter in data[0]:
        counter += 1
        if counter <= (length - 1):
            underscores += " \_"



    e = discord.Embed(color=discord.Color.random(), title=data[0], description=f'{data[1][0]}{underscores}')
    e.set_footer(text='Be the first to unscramble this word and earn points for your profile!')
    e.set_author(name=random.choice(titles))
    await ctx.send(embed = e)
    await check_word(self, ctx, data, incorrectCounter)






class AutoGames(commands.Cog):
    """WIP"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def trig(self, ctx):
        await send_word(self, ctx)


def setup(bot):
    bot.add_cog(AutoGames(bot))