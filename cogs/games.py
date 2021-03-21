import asyncio
import discord    
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
import random


class ChatGames(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    async def fight(self, ctx, user: discord.Member):
        turn = 0 #adding a turn variable for turn taking
        authorhealth = 12
        userhealth = 12
        choices = ["punch", "insult", "pray"]
        punchdmg = [1, 1.5, 1.5, 2, 2, 2.5, 3, 5]
        praydmg = [-1, -1, 2, 4, -10, 15]
         
        if user == ctx.author:
            await ctx.send(f"You can't fight yourself, {ctx.author.mention}.")
        else:
            try:    
                await ctx.send(f"{ctx.author.mention} vs {user.mention}, who will win? `o.O`")
                while authorhealth > 0.4 and userhealth > 0.4:

                    if turn == 0:
                        await ctx.send(f"{ctx.author.mention}: Your move! Choices: `{', '.join([choice for choice in choices])}`")
                        def check(m):
                            return m.content in choices and m.author == ctx.message.author
                        response = await self.bot.wait_for('message', check = check, timeout=120)
                        
                        if "punch" in response.content.lower() and turn == 0:#turn == 0 is here since it doesn't work sometimes
                            dmgdone = (random.choice(punchdmg))
                            userhealth = (userhealth - dmgdone)
                       
                            if int(dmgdone) >= 0.5: #0x00FF00 is green
                                if int(dmgdone) <= 2.5:
                                    c = 0xffa500
                            if int(dmgdone) >= 3:
                                c = 0xff0000

                            
                            e = discord.Embed(color=c, title='Nice punch!')
                            e.description=(f'{ctx.author.name} did {dmgdone} damage!')
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            await ctx.send(embed=e)
                            
                            turn = turn + 1

                        if "pray" in response.content.lower() and turn == 0:#turn == 0 is here since it doesn't work sometimes
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
                            e.description=(d)
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            await ctx.send(embed=e)
                            
                            turn = turn + 1

                    elif turn == 1:
                        await ctx.send(f"{user.mention}: Your move! Choices: `{', '.join([choice for choice in choices])}`")
                        def check(o):
                            return o.content in choices and o.author == user
                        response = await self.bot.wait_for('message', check = check, timeout=120)
                        
                        if "punch" in response.content.lower() and turn == 1:#turn == 0 is here since it doesn't work sometimes
                            dmgdone = (random.choice(punchdmg))
                            authorhealth = (authorhealth - dmgdone)
                            
                            if int(dmgdone) >= 0.5: #0x00FF00 is green
                                if int(dmgdone) <= 2.5:
                                    c = 0xffa500
                            if int(dmgdone) >= 3:
                                c = 0xff0000
                            
                            e = discord.Embed(color=c, title='Nice punch!')
                            e.description=(f'{user.name} did {dmgdone} damage!')
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            await ctx.send(embed=e)
                            
                            turn = turn - 1
                        

                        if "pray" in response.content.lower() and turn == 1:#turn == 0 is here since it doesn't work sometimes
                            dmgdone = (random.choice(praydmg))
                            userhealth = (userhealth - dmgdone)
                     
                            if int(dmgdone) < 0:
                                c = 0x00FF00
                                title = ['The gods gave you mercy', 'Its your lucky day!', 'GG']
                                t = (random.choice(title))
                                d = f'{user.name} gained health!'
                            else:
                                c = 0xff0000
                                title = ['\"You pathetic mortal\" - God', '\"You suck\" - God', '\"Today is not your day\" - God']
                                t = (random.choice(title))
                                d = f'{user.name} lost health due to a failed prayer :('

                            
                            e = discord.Embed(color=c, title=t)
                            e.description=(d)
                            e.add_field(name=f'{ctx.author.name}', value=f'{authorhealth} HP')
                            e.add_field(name=f'{user.name}', value=f'{userhealth} HP')
                            await ctx.send(embed=e)
                            
                            turn = turn - 1


                if turn == 0:
                    whoWon = user
                else:
                    whoWon = ctx.author
                e = discord.Embed(color=0, title='Results')
                e.description=(f'{whoWon.mention} won!!')
                e.add_field(name=f'{ctx.author.name}\'s health', value=f'{authorhealth} HP')
                e.add_field(name=f'{user.name}\'s health', value=f'{userhealth} HP')
                return await ctx.send(embed=e)
            except asyncio.exceptions.TimeoutError:
                if turn == 1:
                    return await ctx.send(f'**{user} did not respond in time... CHICKEN**')
                else:
                    return await ctx.send(f'**{ctx.author} did not respond in time... CHICKEN**')
                    




def setup(bot):
    bot.add_cog(ChatGames(bot))