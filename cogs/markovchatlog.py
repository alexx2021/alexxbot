import re
import string

import discord

from discord.ext import commands

guildlist = [812951618945286185, 741054230370189343, 812520226603794432, 804063441778114620]
# iridescent
# alexx bot
# minty club
# bot test
class ChatLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        await self.bot.wait_until_ready()
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        if message.author.bot:
            if message.author.id == 64186055052702517:
                pass
            else:
                return
        if message.channel.id == 741054231661903907:
            return
        if not message.guild:
            return
        if message.guild.id not in guildlist:
            return

        record = self.clean_message(message.clean_content)
        if record:
            await self.bot.mark.execute('INSERT INTO chatlogs VALUES (?, ?)', (message.guild.id, record))
            await self.bot.mark.commit()

    def clean_message(self, message):
        """Cleans the message of unnecessary information.
        Args:
            message (str): Message from the chat to modify.
        Returns:
            text (str): Text that has URLs, mentions, and punctuation removed.
        """
        text = message.lower()
        text = text.replace('codex', '')
        text = re.sub(r'''(\s)\#\w+''', '', text)
        text = re.sub(
            r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)'''
            r'''(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+'''
            r'''(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|'''
            r'''[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', '', text
        )
        depunctuate = str.maketrans('', '', string.punctuation)
        text = text.translate(depunctuate)
        text = ' '.join(text.split())
        return text



    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpMark(self, ctx):
        rows = await self.bot.mark.execute_fetchall("SELECT message FROM chatlogs WHERE guild_id = ?", (ctx.guild.id,))
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')


def setup(bot):
    bot.add_cog(ChatLog(bot))