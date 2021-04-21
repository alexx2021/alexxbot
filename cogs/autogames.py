import asyncio
from collections import defaultdict
import discord
from discord.ext import commands, tasks
from random import randint, shuffle
import random
import time

async def are_lvls_enabled(self, guild):
    try:
        enabled = self.bot.arelvlsenabled[f"{guild.id}"]
        if 'TRUE' in enabled:
            return True
        else:
            return False
    except KeyError:
        return False

async def give_xp(self, message):
    query = 'SELECT * FROM xp WHERE guild_id = ? AND user_id = ?' 
    gid = message.guild.id
    uid = message.author.id
    params = (gid, uid)
    member = await self.bot.xp.execute_fetchall(query, params)
    if member:
        xp = member[0][2]
        level = (int (xp ** (1/3.25)))
        if xp == 0.5:
            new_xp = xp + 0.5
        elif xp < 30:
            if xp >= 1:
                xpToAdd = randint(2, 5)
                new_xp = xp + xpToAdd
        else:
            xpToAdd = randint(15, 25)
            new_xp = xp + round(((level * xpToAdd) / randint(2,3)))
        
        query = 'UPDATE xp SET user_xp = ? WHERE guild_id = ? AND user_id = ?'
        params = (new_xp, gid, uid)
        await self.bot.xp.execute(query, params)
        await self.bot.xp.commit()
        return (new_xp - xp)
    else:
        await self.bot.xp.execute('INSERT INTO xp VALUES(?,?,?)',(gid, uid, 1))
        await self.bot.xp.commit()
        return 1

###########################################################################UNSCRAMBLE

async def scramble_word():
    words = ['hello', 'goodbye', 'discord', 'alex','boost',
    'online','offline', 'nitro', 'bot', 'server','goat',
    'apple', 'pear', 'strawberry', 'chocolate',
    'love', 'button', 'boat', 'taco', 'elephant', 'bird',
    'duck', 'fox', 'music', 'word', 'scramble', 'egg', 'potato',
    'tomato','apple', 'lemon', 'carrot', 'cherry', 'pig', 'cow',
    'math', 'coat', 'shirt', 'sad', 'smile', 'turkey', 'ant', 'cookie',
    'chicken', 'cat', 'melon', 'mango', 'coffee', 'chicken'
    ]
    word = random.choice(words)
    unscram = word
    word = list(word)
    shuffle(word)
    scram = ''.join(word)
    returnList = [scram, unscram]
    return returnList

async def check_word(self, message, data, counter):
    try:    
        def check(msgcheck):
            return msgcheck.channel == message.channel and not msgcheck.author.bot
        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if data[1] in msg.content.lower():
            if await are_lvls_enabled(self, message.guild):
                xpAmt = await give_xp(self, message)
                return await msg.reply(f'🎉 **{msg.author.name}** got the word correct first, and earned **{xpAmt}** xp!')
            else:
                return await msg.reply(f'🎉 **{msg.author.name}** got the word correct first!')
        else:
            counter += 1 
            if counter > 20:
                return await message.channel.send('No one got the correct answer in time :(')
            else:
                #print(counter)
                await check_word(self, message, data, counter)
    except asyncio.exceptions.TimeoutError:
        return await message.channel.send('No one replied in time :(')


async def send_word(self, message):
    self.bot.autogames[message.guild.id].update({"ongoing": 1})
    self.bot.autogames[message.guild.id].update({"lastrun": time.time()})


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



    e = discord.Embed(color=discord.Color.random(), description=f'`{data[0]}`\n{data[1][0]}{underscores}')
    e.set_footer(text='Be the first to unscramble this word and earn xp (if it\'s enabled)!')
    e.set_author(name=random.choice(titles))
    await message.channel.send(embed = e)
    await check_word(self, message, data, incorrectCounter)
    self.bot.autogames[message.guild.id].update({"ongoing": 0})

###########################################################################GUESS THE NUMBER
async def generate_number():
    data = randint(1, 10)
    return data

async def check_number(self, message, data, counter):
    try:    
        def check(msgcheck):
            return msgcheck.channel == message.channel and not msgcheck.author.bot
        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if msg.content.startswith(str(data)):
            if await are_lvls_enabled(self, message.guild):
                xpAmt = await give_xp(self, message)
                return await msg.reply(f'🎉 **{msg.author.name}** got the number correct first, and earned **{xpAmt}** xp!')
            else:
                return await msg.reply(f'🎉 **{msg.author.name}** got the number correct first!')
        else:
            counter += 1 
            if counter > 25:
                return await message.channel.send('No one got the correct answer in time :(')
            else:
                #print(counter)
                await check_number(self, message, data, counter)
    except asyncio.exceptions.TimeoutError:
        return await message.channel.send('No one replied in time :(')


async def send_number(self, message):
    self.bot.autogames[message.guild.id].update({"ongoing": 1})
    self.bot.autogames[message.guild.id].update({"lastrun": time.time()})


    incorrectCounter = 0
    titles = ['❗  GTN Event!', '🤔  Guess the number!','🥺  Pls guess!' ]
    data = await generate_number()
    

    e = discord.Embed(color=discord.Color.random(), description='Number is between 1 and 10.')
    e.set_footer(text='Be the first to guess the number and earn xp (if it\'s enabled)!')
    e.set_author(name=random.choice(titles))
    await message.channel.send(embed = e)
    await check_number(self, message, data, incorrectCounter)
    self.bot.autogames[message.guild.id].update({"ongoing": 0})




#####################################################################RETYPE BACKWARDS NUMBER
async def generate_backwards_number():
    data = randint(100000000000, 999999999999)
    data2 = list(str(data))
    data2.reverse()
    newData = ''
    for num in data2:
        newData += num
    return [newData, data]

async def check_backwards_number(self, message, data, counter):
    try:    
        def check(msgcheck):
            return msgcheck.channel == message.channel and not msgcheck.author.bot
        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if msg.content.startswith(str(data[0])):
            if await are_lvls_enabled(self, message.guild):
                xpAmt = await give_xp(self, message)
                return await msg.reply(f'🎉 **{msg.author.name}** got the number correct first, and earned **{xpAmt}** xp!')
            else:
                return await msg.reply(f'🎉 **{msg.author.name}** got the number correct first!')
        else:
            counter += 1 
            if counter > 20:
                return await message.channel.send('No one got the correct answer in time :(')
            else:
                #print(counter)
                await check_backwards_number(self, message, data, counter)
    except asyncio.exceptions.TimeoutError:
        return await message.channel.send('No one replied in time :(')


async def send_backwards_number(self, message):
    self.bot.autogames[message.guild.id].update({"ongoing": 1})
    self.bot.autogames[message.guild.id].update({"lastrun": time.time()})


    incorrectCounter = 0
    titles = ['❗  Typing Event!', '🤔  Send the number!','🥺  Pls do this asap!' ]
    data = await generate_backwards_number()
    

    e = discord.Embed(color=discord.Color.random(), description=f'`{data[1]}`\nRetype the number above back into chat **>Backwards<**!')
    e.set_footer(text='Be the first to retype the number and earn xp (if it\'s enabled)!')
    e.set_author(name=random.choice(titles))
    await message.channel.send(embed = e)
    await check_backwards_number(self, message, data, incorrectCounter)
    self.bot.autogames[message.guild.id].update({"ongoing": 0})
#####################################################################MATH PROBLEM
async def generate_math():
    num1 = randint(0,15)
    num2 = randint(0,15)
    ops = ["*","-","+"]
    operator = random.choice(ops)
    if operator == "*":
        correctAnswer = (num1 * num2)
    if operator == "+":
        correctAnswer = (num1 + num2)
    if operator == "-":
        correctAnswer = (num1 - num2)

    return [num1, operator, num2, correctAnswer]

async def check_math(self, message, data, counter):
    try:    
        def check(msgcheck):
            return msgcheck.channel == message.channel and not msgcheck.author.bot
        msg = await self.bot.wait_for('message', check=check, timeout=120)
        if msg.content.startswith(str(data[3])):
            if await are_lvls_enabled(self, message.guild):
                xpAmt = await give_xp(self, message)
                return await msg.reply(f'🎉 **{msg.author.name}** got the problem correct first, and earned **{xpAmt}** xp!')
            else:
                return await msg.reply(f'🎉 **{msg.author.name}** got the problem correct first!')
        else:
            counter += 1 
            if counter > 20:
                return await message.channel.send('No one got the correct answer in time :(')
            else:
                #print(counter)
                await check_math(self, message, data, counter)
    except asyncio.exceptions.TimeoutError:
        return await message.channel.send('No one replied in time :(')


async def send_math(self, message):
    self.bot.autogames[message.guild.id].update({"ongoing": 1})
    self.bot.autogames[message.guild.id].update({"lastrun": time.time()})


    incorrectCounter = 0
    titles = ['❗  Math Event!', '🤔  Solve the problem!','🥺  Pls math asap!' ]
    data = await generate_math()
    

    e = discord.Embed(color=discord.Color.random(), description=f'`{data[0]} {data[1]} {data[2]}`')
    e.set_footer(text='Be the first to solve the problem and earn xp (if it\'s enabled)!')
    e.set_author(name=random.choice(titles))
    await message.channel.send(embed = e)
    await check_math(self, message, data, incorrectCounter)
    self.bot.autogames[message.guild.id].update({"ongoing": 0})
#####################################################################REACT FIRST
async def generate_emoji():
    r = randint(1,4)
    if r == 1:
        reac = "⬅️"
        name = "left"
    elif r == 2:
        reac = "➡️"
        name = "right"
    elif r == 3:
        reac = "⬆️"
        name = "up"
    elif r == 4:
        reac = "⬇️"
        name = "down"
    return [reac, name]

async def generate_random_sequence(theEmbed):
    dic = {1:"⬅️", 2:"➡️", 3:"⬆️",4:"⬇️"}
    c = random.choice(list(dic))
    await theEmbed.add_reaction(dic[c])
    dic.pop(c)
    
    c = random.choice(list(dic))
    await theEmbed.add_reaction(dic[c])
    dic.pop(c)
    
    c = random.choice(list(dic))
    await theEmbed.add_reaction(dic[c])
    dic.pop(c)
    
    c = random.choice(list(dic))
    await theEmbed.add_reaction(dic[c])
    dic.pop(c)



async def check_reaction(self, message, data, theEmbed, reactedBefore, antireactspam):
    try:
        if reactedBefore == 0:
            await generate_random_sequence(theEmbed)
            reactedBefore = 1    

        reaction, person = await self.bot.wait_for(
                        "reaction_add",
                        timeout=120,
                        check=lambda reaction, user: user != self.bot.user and reaction.message.channel == message.channel)
                
        if str(reaction.emoji) == data[0]:
            if await are_lvls_enabled(self, message.guild):
                if antireactspam[person.id] != 1:
                    antireactspam[person.id] = 1
                    xpAmt = await give_xp(self, message)
                    return await message.channel.send(f'🎉 **{person.mention}** reacted correctly first, and earned **{xpAmt}** xp!')
                else:
                    await check_reaction(self, message, data, theEmbed, reactedBefore, antireactspam)
            else:
                if antireactspam[person.id] != 1:
                    antireactspam[person.id] = 1
                    return await message.channel.send(f'🎉 **{person.mention}** reacted correctly first!')
                else:
                    await check_reaction(self, message, data, theEmbed, reactedBefore, antireactspam)
        else:
            if antireactspam[person.id] != 1:
                antireactspam[person.id] = 1
                await message.channel.send(f':frowning:  **{person.mention}** reacted with the wrong emoji!')
            await check_reaction(self, message, data, theEmbed, reactedBefore, antireactspam)
    except asyncio.exceptions.TimeoutError:
        return await message.channel.send('No one reacted in time :(')

async def send_react(self, message):
    self.bot.autogames[message.guild.id].update({"ongoing": 1})
    self.bot.autogames[message.guild.id].update({"lastrun": time.time()})

    titles = ['❗  React Event!', '🤔  Are you fast enough?!','🥺  Pls asap!' ]
    data = await generate_emoji()
    
    def def_value():
        return 0
    reactedBefore = 0
    antireactspam = defaultdict(def_value)
    

    e = discord.Embed(color=discord.Color.random(), description=f'React to `{data[1]}`!')
    e.set_footer(text='Be the first to react to the correct emoji and earn xp (if it\'s enabled)!')
    e.set_author(name=random.choice(titles))
    theEmbed = await message.channel.send(embed = e)
    await check_reaction(self, message, data, theEmbed, reactedBefore, antireactspam)
    self.bot.autogames[message.guild.id].update({"ongoing": 0})

async def active_users_pop(self, msg):
    try:
        self.bot.autogames[msg.guild.id].pop(1)
    except KeyError:
        pass
    try:
        self.bot.autogames[msg.guild.id].pop(2)
    except KeyError:
        pass
    try:
        self.bot.autogames[msg.guild.id].pop(3)
    except KeyError:
        pass
    #print('popped')

async def check_1(self, msg):
        try:
            if self.bot.autogames[msg.guild.id][1]:
                return True
        except KeyError:
            return False
async def check_2(self, msg):
        try:
            if self.bot.autogames[msg.guild.id][2]:
                return True
        except KeyError:
            return False
async def check_3(self, msg):
        try:
            if self.bot.autogames[msg.guild.id][3]:
                return True
        except KeyError:
            return False

class AutoGames(commands.Cog):
    """WIP"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(hidden = True)
    @commands.is_owner()
    async def insert(self, ctx):
        try:
            self.bot.autogames.pop(ctx.guild.id)
        except KeyError:
            pass

        self.bot.autogames.update({ctx.guild.id : {"channel_id": ctx.channel.id, "lastrun": 0, "ongoing": 0}})


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.bot.wait_until_ready()

        if not message.guild:
            return
        if message.author.bot:
            return
        guild = message.guild.id

        try:
            lastrun = self.bot.autogames[guild]["lastrun"]
            ch_id = self.bot.autogames[guild]["channel_id"]
            ongoing = self.bot.autogames[guild]["ongoing"]
            delay = self.bot.autogames[guild]["delay"]
            if ch_id == message.channel.id:
                if not await check_1(self, message):
                    self.bot.autogames[guild][1] = message.author.id
                    #print('1')
                elif not await check_2(self, message):
                    if self.bot.autogames[guild][1] == message.author.id:
                        pass
                    else:
                        self.bot.autogames[guild][2] = message.author.id
                        #print('2')
                elif not await check_3(self, message):
                    if self.bot.autogames[guild][1] == message.author.id:
                        pass
                    elif self.bot.autogames[guild][2] == message.author.id:
                        pass
                    else:
                        self.bot.autogames[guild][3] = message.author.id
                        #print('3')

                perms = message.channel.permissions_for(message.guild.me)
                if perms.send_messages:
                    if (lastrun < (time.time() - (delay * 60)) and (ongoing != 1)) and (await check_1(self, message)) and (await check_2(self, message) and (await check_3(self, message))):
                        game = randint(1, 7)
                        if game == 1:
                            await active_users_pop(self, message)
                            return await send_word(self, message)
                        elif game == 2:
                            await active_users_pop(self, message)
                            return await send_number(self, message)
                        elif game == 3:
                            await active_users_pop(self, message)
                            return await send_backwards_number(self, message)
                        elif game == 4:
                            await active_users_pop(self, message)
                            return await send_math(self, message)
                        elif game == 5:
                            if perms.add_reactions:
                                await active_users_pop(self, message)
                                return await send_react(self, message)
                        else:
                            pass
        except KeyError:
            pass




def setup(bot):
    bot.add_cog(AutoGames(bot))