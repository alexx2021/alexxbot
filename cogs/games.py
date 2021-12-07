import asyncio
import time
import aiohttp
import discord
from discord.embeds import Embed    
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random
import rapidfuzz
from discord.ext.commands.core import bot_has_permissions



class games(commands.Cog):
    """🎮 Games to play with your friends"""
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(6.0, 10.0, commands.BucketType.user)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True    
    
    
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @bot_has_permissions(add_reactions=True)
    @commands.command(help='Battle a user of your choice in this interactive game!')
    async def deathbattle(self, ctx, user: discord.Member):
        turn = 0 #adding a turn variable for turn taking
        authorhealth = 15
        userhealth = 15
        choices = ["punch", "insult", "pray", "surrender"]
        punchdmg = [1, 1, 1, 1.5, 2, 3]
        praydmg = [-1, -2, -2, 2, 6, -10, 15]
        insultoutcomes = [True, True, False, False, False, False]

        #do I have manage messages?
        perms = ctx.channel.permissions_for(ctx.guild.me)
        
        if user.bot:
            return await ctx.send(f"<a:x_:826577785173704754> You can't fight bots, {ctx.author.mention}.")
        if user == ctx.author:
            return await ctx.send(f"<a:x_:826577785173704754> You can't fight yourself, {ctx.author.mention}.")
        else:
            try:    
                e = discord.Embed(color=0, title='Deathbattle')
                e.description=(f'{ctx.author.mention} vs {user.mention}, who will win? `o.O`')
                e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                e.set_footer(text=f'It is {ctx.author.name}\'s turn')
                gamemsg = await ctx.send(embed=e)
                await gamemsg.add_reaction("👊")
                await asyncio.sleep(0.25)
                await gamemsg.add_reaction("😡")
                await asyncio.sleep(0.25)
                await gamemsg.add_reaction("🙏")
                await asyncio.sleep(0.25)
                await gamemsg.add_reaction("⬜")

                await ctx.send(f"**React to make your move**.\n----------\n👊 to punch (1-3 dmg, no risk)\n----------\n😡 to insult (if you fail you loose your turn :O)(otherwise -5 HP for other player + an extra turn) \n----------\n🙏 to pray (high risk, high reward, the gods will decide whether to heal or hurt you)\n----------\n⬜ to surrender")
                
                while authorhealth > 0.4 and userhealth > 0.4:
                    reactionuser = user
                    reactionauthor = ctx.author

                    if turn == 0:
                        reaction, member = await self.bot.wait_for(
                            "reaction_add",
                            timeout=60,
                            check=lambda reaction, user: user == ctx.author
                            and reaction.message.channel == ctx.channel
                        )
                        
                        if str(reaction.emoji) == "👊" and turn == 0:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("👊", member)
                            dmgdone = (random.choice(punchdmg))
                            userhealth = (userhealth - dmgdone)
                            c = 0xffa500

                            
                            e = discord.Embed(color=c, title='Nice punch!')
                            e.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
                            e.description=(f'{ctx.author.name} did {dmgdone} damage!')
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            e.set_footer(text=f'It is {user.name}\'s turn now')
                            await gamemsg.edit(embed=e)
                            
                            turn = turn + 1

                        if str(reaction.emoji) == "🙏" and turn == 0:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("🙏", member)
                            dmgdone = (random.choice(praydmg))
                            authorhealth = (authorhealth - dmgdone)
                     
                            if int(dmgdone) < 0:
                                c = 0x00FF00
                                title = ['The gods gave you mercy', 'Its your lucky day!', 'GG', 'You lucky duck']
                                t = (random.choice(title))
                                d = f'{ctx.author.name} gained health due to a successful prayer!'
                            else:
                                c = 0xff0000
                                title = ['\"You pathetic mortal\" - God', '\"You suck\" - God', '\"Today is not your day\" - God', '\"lol\" - God']
                                t = (random.choice(title))
                                d = f'{ctx.author.name} lost health due to a failed prayer :('

                            e = discord.Embed(color=c, title=t)
                            e.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
                            e.description=(d)
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            e.set_footer(text=f'It is {user.name}\'s turn now')
                            await gamemsg.edit(embed=e)

                            turn = turn + 1
                            
                        
                        if str(reaction.emoji) == "😡" and turn == 0:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("😡", member)
                            insulted = (random.choice(insultoutcomes))

                            if insulted is True:
                                turn = turn + 0 #You get 1 more turn
                                userhealth = (userhealth - 5)
                                c = 0x00FF00
                                title = ['You called their momma fat', 'You told them that they would never amount to anything', 'You told them they suck', 'You pointed out their lack of a life']
                                t = (random.choice(title))
                                d = f'{ctx.author.name} gave {user.name} an existential crisis for the **next turn**\nas well as 5 damage done'
                                f = f'It is {ctx.author.name}\'s turn now'
                            if insulted is False:
                                turn = turn + 1
                                c = 0xff0000
                                title = ['You tried to make fun of their rainbow socks', 'You tried to be toxic', 'You could not come up with an insult in time']
                                t = (random.choice(title))
                                d = f'{ctx.author.name} failed to do any real emotional damage'
                                f = f'It is {user.name}\'s turn now'

                            
                            e = discord.Embed(color=c, title=t)
                            e.set_author(name=f"{ctx.author}", icon_url=ctx.author.display_avatar.url)
                            e.description=(d)
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            e.set_footer(text=f)
                            await gamemsg.edit(embed=e)

                        if str(reaction.emoji) == "⬜" and turn == 0:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("⬜", member)
                            break
                            


                            

                    elif turn == 1:
                        reaction, member = await self.bot.wait_for(
                            "reaction_add",
                            timeout=60,
                            check=lambda reaction, user: user == reactionuser
                            and reaction.message.channel == ctx.channel
                        )
                        
                        if str(reaction.emoji) == "👊" and turn == 1:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("👊", member)
                            dmgdone = (random.choice(punchdmg))
                            authorhealth = (authorhealth - dmgdone)
                            c = 0xffa500
                            
                            e = discord.Embed(color=c, title='Nice punch!')
                            e.set_author(name=f"{user}", icon_url=user.display_avatar.url)
                            e.description=(f'{user.name} did {dmgdone} damage!')
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            e.set_footer(text=f'It is {ctx.author.name}\'s turn now')
                            await gamemsg.edit(embed=e)
                            
                            turn = turn - 1
                        

                        if str(reaction.emoji) == "🙏" and turn == 1:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("🙏", member)
                            dmgdone = (random.choice(praydmg))
                            userhealth = (userhealth - dmgdone)
                     
                            if int(dmgdone) < 0:
                                c = 0x00FF00
                                title = ['The gods gave you mercy', 'Its your lucky day!', 'GG']
                                t = (random.choice(title))
                                d = f'{user.name} gained health due to a successful prayer!'
                            else:
                                c = 0xff0000
                                title = ['\"You pathetic mortal\" - God', '\"You suck\" - God', '\"Today is not your day\" - God']
                                t = (random.choice(title))
                                d = f'{user.name} lost health due to a failed prayer :('

                            
                            e = discord.Embed(color=c, title=t)
                            e.set_author(name=f"{user}", icon_url=user.display_avatar.url)
                            e.description=(d)
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            e.set_footer(text=f'It is {ctx.author.name}\'s turn now')
                            await gamemsg.edit(embed=e)

                            turn = turn - 1
                            

                        if str(reaction.emoji) == "😡" and turn == 1:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("😡", member)
                            insulted = (random.choice(insultoutcomes))

                            if insulted is True:
                                turn = turn + 0 #You get 1 more turn
                                authorhealth = (authorhealth - 5)
                                c = 0x00FF00
                                title = ['You called their momma fat', 'You told them that they would never amount to anything', 'You told them they suck', 'You pointed out their lack of a life']
                                t = (random.choice(title))
                                d = f'{user.name} gave {ctx.author.name} an existential crisis for the **next turn**\nas well as 5 damage done'
                                f = f'It is {user.name}\'s turn now'
                            if insulted is False:
                                turn = turn - 1
                                c = 0xff0000
                                title = ['You tried to make fun of their rainbow socks', 'You tried to be toxic', 'You could not come up with an insult in time']
                                t = (random.choice(title))
                                d = f'{user.name} failed to do any real emotional damage'
                                f = f'It is {ctx.author.name}\'s turn now'

                            
                            e = discord.Embed(color=c, title=t)
                            e.set_author(name=f"{user}", icon_url=user.display_avatar.url)
                            e.description=(d)
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            e.set_footer(text=f)
                            await gamemsg.edit(embed=e)


                        if str(reaction.emoji) == "⬜" and turn == 1:
                            if perms.manage_messages:
                                await gamemsg.remove_reaction("⬜", member)
                            break

                await asyncio.sleep(1)
                if userhealth > authorhealth:
                    whoWon = user.mention
                if authorhealth > userhealth:
                    whoWon = ctx.author.mention
                if authorhealth == userhealth:
                    whoWon = "No one"

                e = discord.Embed(color=0, title='Results')
                e.description=(f'{whoWon} won!!')
                e.add_field(name=f'{ctx.author.name}\'s health', value=f'{authorhealth} HP')
                e.add_field(name=f'{user.name}\'s health', value=f'{userhealth} HP')
                return await gamemsg.edit(embed=e)
            except asyncio.exceptions.TimeoutError:
                if turn == 1:
                    return await ctx.send(f'**{user} did not react in time... CHICKEN**')
                else:
                    return await ctx.send(f'**{ctx.author} did not react in time... CHICKEN**')

    #minesweeper owo
    @commands.guild_only()
    @commands.command(help=('Randomly generated minesweeper game!'))
    async def tacosweeper(self, ctx, columns = None, rows = None, tacos = None):
        if columns is None or rows is None and tacos is None:
            if columns is not None or rows is not None or tacos is not None:
                
                errortxt = ('That is not formatted properly or valid positive integers weren\'t used, ',
                'the proper format is:\n`[Prefix]minesweeper <columns> <rows> <tacos>`\n\n',
                'You can give me nothing for random columns, rows, and tacos.')
                errortxt = ''.join(errortxt)

                await ctx.send(errortxt)
                return
            else:
                columns = random.randint(4,13)
                rows = random.randint(4,13)
                tacos = columns * rows - 1
                tacos = tacos / 2.5
                tacos = round(random.randint(5, round(tacos)))
        try:
            columns = int(columns)
            rows = int(rows)
            tacos = int(tacos)
        except ValueError:
            await ctx.send(errortxt)
            return
        if columns > 13 or rows > 13:
            await ctx.send('The limit for the columns and rows are 13 due to discord limits...')
            return
        if columns < 1 or rows < 1 or tacos < 1:
            await ctx.send('The provided numbers cannot be zero or negative...')
            return
        if tacos + 1 > columns * rows:
            await ctx.send(':boom:**BOOM**, you have more tacos than spaces on the grid or you attempted to make all of the spaces tacos!')
            return

        grid = [[0 for num in range (columns)] for num in range(rows)]

        loop_count = 0
        while loop_count < tacos:
            x = random.randint(0, columns - 1)
            y = random.randint(0, rows - 1)

            if grid[y][x] == 0:
                grid[y][x] = 'B'
                loop_count = loop_count + 1

            if grid[y][x] == 'B':
                pass

        pos_x = 0
        pos_y = 0
        while pos_x * pos_y < columns * rows and pos_y < rows:
            adj_sum = 0
            for (adj_y, adj_x) in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,1),(1,-1),(-1,-1)]:
                try:
                    if grid[adj_y + pos_y][adj_x + pos_x] == 'B' and adj_y + pos_y > -1 and adj_x + pos_x > -1:
                        adj_sum = adj_sum + 1
                except Exception as error:
                    pass
            if grid[pos_y][pos_x] != 'B':
                grid[pos_y][pos_x] = adj_sum

            if pos_x == columns - 1:
                pos_x = 0
                pos_y = pos_y + 1
            else:
                pos_x = pos_x + 1

        string_builder = []
        for the_rows in grid:
            string_builder.append(''.join(map(str, the_rows)))
        string_builder = '\n'.join(string_builder)

        string_builder = string_builder.replace('0', '||:zero:||')
        string_builder = string_builder.replace('1', '||:one:||')
        string_builder = string_builder.replace('2', '||:two:||')
        string_builder = string_builder.replace('3', '||:three:||')
        string_builder = string_builder.replace('4', '||:four:||')
        string_builder = string_builder.replace('5', '||:five:||')
        string_builder = string_builder.replace('6', '||:six:||')
        string_builder = string_builder.replace('7', '||:seven:||')
        string_builder = string_builder.replace('8', '||:eight:||')
        final = string_builder.replace('B', '||:taco:||')

        percentage = columns * rows
        percentage = tacos / percentage
        percentage = 100 * percentage
        percentage = round(percentage, 2)

        embed = discord.Embed(title='\U0001F642 Tacosweeper \U0001F635', color=0xC0C0C0)
        embed.add_field(name='Columns:', value=columns, inline=True)
        embed.add_field(name='Rows:', value=rows, inline=True)
        embed.add_field(name='Total Spaces:', value=columns * rows, inline=True)
        embed.add_field(name='Taco Count:', value=tacos, inline=True)
        embed.add_field(name='Taco Percentage:', value=f'{percentage}%', inline=True)
        embed.add_field(name='Requested by', value=ctx.author.display_name, inline=True)
        await ctx.send(content=f'\U0000FEFF\n{final}', embed=embed)

    @tacosweeper.error
    async def tacosweeper_error(self, ctx, error):
        
        errortxt = ('That is not formatted properly or valid positive integers weren\'t used, ',
                'the proper format is:\n`[Prefix]tacosweeper <columns> <rows> <tacos>`\n\n',
                'You can give me nothing for random columns, rows, and tacos.')
        errortxt = ''.join(errortxt)

        await ctx.send(errortxt)
        return

    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.command(help='How fast do you type?')
    async def typeracer(self, ctx):
        zeroWidth = "​"
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.alexx.lol/random/word/10') as r: 
                data = await r.json()
                if r.status != 200:
                    data = {
                            "words":[
                                "an",
                                "error",
                                "occurred",
                                "getting",
                                "words",
                                "from",
                                "the",
                                "API",
                            ]
                        }
            
        WordList = ""
        unTamperedWordList = ""

        zwCount = random.randrange(0,20)
        randomZeroWidth = ""
        while zwCount >= 0:
            randomZeroWidth = randomZeroWidth + zeroWidth
            zwCount = zwCount - 1
            

        for word in data["words"]:
            WordList = WordList + f"{word} {randomZeroWidth}"
            unTamperedWordList = unTamperedWordList + f"{word} "


        await ctx.send(f'{ctx.author.mention}\nQuick! Type this list of words as fast and as accurate as you can!\n\n**{WordList}**')
        start = time.time()
        
        def check(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author and (message.content == unTamperedWordList or (rapidfuzz.fuzz.ratio(unTamperedWordList, message.content) > 90))
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            end = time.time()

            totalSeconds = round(end - start)
            totalMinutes = round(totalSeconds / 60, 2)
            
                    
            await ctx.send(f'{ctx.author.mention} **WPM:** {round(10/totalMinutes , 2)} **Accuracy:** {round(rapidfuzz.fuzz.ratio(unTamperedWordList, msg.content), 2)}%')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'{ctx.author.mention}, You did not finish or type it correctly in time.')

                    




def setup(bot):
    bot.add_cog(games(bot))
