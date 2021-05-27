import asyncio
import time
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
        self.bot.quotes = {
            'Life is what happens when you are busy making other plans.': 'L i f e   i s   w h a t   h a p p e n s   w h e n   y o u   a r e   b u s y   m a k i n g   o t h e r   p l a n s.',
            'The greatest glory in living lies not in never falling, but in rising every time we fall.': 'T h e   g r e a t e s t   g l o r y   i n   l i v i n g   l i e s   n o t   i n   n e v e r   f a l l i n g,   b u t   i n   r i s i n g   e v e r y   t i m e   w e   f a l l.',
            'The way to get started is to quit talking and begin doing.':'T h e   w a y   t o   g e t   s t a r t e d   i s   t o   q u i t   t a l k i n g   a n d   b e g i n   d o i n g.',
            'When you reach the end of your rope, tie a knot in it and hang on.':'W h e n   y o u   r e a c h   t h e   e n d   o f   y o u r   r o p e,   t i e   a   k n o t   i n   i t   a n d   h a n g   o n.',
            'Tell me and I forget. Teach me and I remember. Involve me and I learn.':'T e l l   m e   a n d   I   f o r g e t.   T e a c h   m e   a n d   I   r e m e m b e r.   I n v o l v e   m e   a n d   I   l e a r n.',
            'The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart.': 'T h e   b e s t   a n d   m o s t   b e a u t i f u l   t h i n g s   i n   t h e   w o r l d   c a n n o t   b e   s e e n   o r   e v e n   t o u c h e d   -   t h e y   m u s t   b e   f e l t   w i t h   t h e   h e a r t.',
            'It is during our darkest moments that we must focus to see the light.':' I t   i s   d u r i n g   o u r   d a r k e s t   m o m e n t s   t h a t   w e   m u s t   f o c u s   t o   s e e   t h e   l i g h t.',
            'You have brains in your head. You have feet in your shoes. You can steer yourself any direction you choose.':'Y o u   h a v e   b r a i n s   i n   y o u r   h e a d.   Y o u   h a v e   f e e t   i n   y o u r   s h o e s.   Y o u   c a n   s t e e r   y o u r s e l f   a n y   d i r e c t i o n   y o u   c h o o s e.',
            'Turn your wounds into wisdom.':'T u r n   y o u r   w o u n d s   i n t o   w i s d o m.',
            'Sing like no one’s listening, love like you’ve never been hurt, dance like nobody’s watching, and live like it’s heaven on earth.':'S i n g   l i k e   n o   o n e ’ s   l i s t e n i n g,   l o v e   l i k e   y o u ’ v e   n e v e r   b e e n   h u r t,   d a n c e   l i k e   n o b o d y ’ s   w a t c h i n g,   a n d   l i v e   l i k e   i t ’ s   h e a v e n   o n   e a r t h.',
            'The way I see it, if you want the rainbow, you gotta put up with the rain.':'T h e   w a y   I   s e e   i t,   i f   y o u   w a n t   t h e   r a i n b o w,   y o u   g o t t a   p u t   u p   w i t h   t h e   r a i n.',
            'Don’t settle for what life gives you; make life better and build something.':'D o n ’ t   s e t t l e   f o r   w h a t   l i f e   g i v e s   y o u;   m a k e   l i f e   b e t t e r   a n d   b u i l d   s o m e t h i n g. ',
        
        
        
        
        }

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
                            e.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
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
                            e.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
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
                            e.set_author(name=f"{ctx.author}", icon_url=ctx.author.avatar_url)
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
                            e.set_author(name=f"{user}", icon_url=user.avatar_url)
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
                            e.set_author(name=f"{user}", icon_url=user.avatar_url)
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
                            e.set_author(name=f"{user}", icon_url=user.avatar_url)
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
        quotekey = random.choice(list(self.bot.quotes.keys()))
        await ctx.send(f'{ctx.author.mention}\nQuick! Type this sentence as fast and as accurate as you can! Ignore the extra spaces and copy it normally.\n\n**{self.bot.quotes[quotekey]}**')
        start = time.time()
        
        def check(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author and (message.content == quotekey or (rapidfuzz.fuzz.ratio(quotekey, message.content) > 90))
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=180)
            end = time.time()

            totalSeconds = round(end - start)
            totalMinutes = round(totalSeconds / 60, 2)
            
            listThing = list(quotekey)
            counter = 1
            spaceCounter = 0
            for l in listThing:
                if l == ' ':
                    if spaceCounter == 0:
                        counter += 1
                        spaceCounter = 1
                if l != ' ':
                    spaceCounter = 0
                    
            await ctx.send(f'{ctx.author.mention} **WPM:** {round(counter/totalMinutes , 2)} **Accuracy:** {round(rapidfuzz.fuzz.ratio(quotekey, msg.content), 2)}%')
        except asyncio.exceptions.TimeoutError:
            return await ctx.send(f'{ctx.author.mention}, You did not finish or type it correctly in time.')

                    




def setup(bot):
    bot.add_cog(games(bot))
