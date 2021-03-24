import random
import re
import string
import logging
import discord
from discord.ext import commands
logger = logging.getLogger('discord')

async def is_wl(ctx):
    guildlist = [812951618945286185, 741054230370189343, 812520226603794432, 804063441778114620]
    # iridescent
    # alexx bot
    # minty club
    # bot test
    guildID = ctx.guild.id
    if guildID in guildlist:
        return True 
    else:
        return False




class MarkovChain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(is_wl)
    @commands.command(help='The bot will speak its mind based on what has been said in the server before')
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def speak(self, ctx): 
        response = await self.create_chain(ctx.guild)

        embed = discord.Embed(colour=discord.Colour.random(), description= response)
        await ctx.send(embed=embed)
        logger.info(msg=f'{ctx.author} ({ctx.author.id}) used markov generator')


    def format_sentence(self, unformatted_sentence):
        """Adds formatting to generated sentence.
        Args:
            unformatted_sentence (str): Unformatted generated sentence.
        Returns:
            formatted_sentence (str): Formatted generated sentence with
                                      first word capitalized and punctation at end.
        """
        punctuation_list = ['!', '?', '.']
        chance = [0.2, 0.1, 0.9]
        formatted_sentence = unformatted_sentence.capitalize()
        punctuation = random.choices(punctuation_list, chance)
        punctuation = str(punctuation[0])
        formatted_sentence = formatted_sentence.rstrip()
        formatted_sentence += punctuation
        return formatted_sentence

    async def create_chain(self, guild):
        """Creates Markov chain from messages stored in the sqlite db and generates sentence.
        Returns:
            markov_sentence (str): Markov chain generated sentence.
        """
        start_words = []
        word_dict = {}
        flag = 1
        count = 0
        messages = await self.bot.mark.execute_fetchall('SELECT message FROM chatlogs WHERE guild_id = ?', (guild.id,))

        for item in messages:
            # reformat messages and split the words into lists
            temp_list = item[0].split()

            # add the first word of each message to a list
            if (
                len(temp_list) > 0 and
                temp_list[0].lower() != self.bot.user.name and
                not temp_list[0].isdigit()
            ):
                start_words.append(temp_list[0])

            # create a dictionary of words that will be used to form the sentence
            for index, item in enumerate(temp_list):
                # add new word to dictionary
                if temp_list[index] not in word_dict:
                    word_dict[temp_list[index]] = []

                # add next word to dictionary
                if (
                    index < len(temp_list) - 1 and
                    temp_list[index + 1].lower() != self.bot.user.name and
                    not temp_list[index + 1].isdigit()
                ):
                    word_dict[temp_list[index]].append(temp_list[index + 1])

        # choose a random word to start the sentence
        curr_word = random.choice(start_words)
        sentence = ''

        # loop through the chain
        while flag == 1 and count < 100:
            # add word to sentence
            count += 1
            sentence += curr_word + ' '

            # choose a random word
            if len(word_dict[curr_word]) != 0:
                curr_word = random.choice(word_dict[curr_word])

            # nothing can follow the current word, end the chain
            elif len(word_dict[curr_word]) == 0:
                flag = 0

        # format final sentence
        markov_sentence = self.format_sentence(sentence)
        return markov_sentence


def setup(bot):
    bot.add_cog(MarkovChain(bot))