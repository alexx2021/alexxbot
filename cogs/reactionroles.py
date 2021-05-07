import asyncio
from utils.utils import get_or_fetch_guild, get_or_fetch_member
import discord
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions, command, has_permissions
from discord.raw_models import RawReactionActionEvent


async def process_reaction(self, payload: RawReactionActionEvent, action=None): # TODO add spam protection
    if payload.guild_id:
        if payload.user_id != 715446479837462548 and payload.user_id != 752585938630082641:
            try:
                self.bot.cache_reactionroles[payload.guild_id][payload.message_id][payload.emoji.name]
                if payload.member:
                    user = payload.member
                    role = user.guild.get_role(int(self.bot.cache_reactionroles[payload.guild_id][payload.message_id][payload.emoji.name]))
                else:
                    guild = await get_or_fetch_guild(self, payload.guild_id)
                    user = await get_or_fetch_member(self, guild, payload.user_id)
                    role = guild.get_role(int(self.bot.cache_reactionroles[payload.guild_id][payload.message_id][payload.emoji.name]))
                    
                if role is None:
                    return
                
                if action == "add":
                    if user.guild.me.top_role.position > role.position:
                        if user.guild.me.guild_permissions.manage_roles:
                            await user.add_roles(role, reason='Reactionrole.')
                if action == "remove":
                    if user.guild.me.top_role.position > role.position:
                        if user.guild.me.guild_permissions.manage_roles:
                            await user.remove_roles(role, reason='Reactionrole.')
            except KeyError:
                return

async def reaction_spam_check(self, payload: RawReactionActionEvent):
    return True

class rr(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

 
    

    @commands.is_owner()
    @commands.command()
    async def dumprrr(self, ctx):
        async with self.bot.db.acquire() as connection:
            roles = await connection.fetch("SELECT * FROM reactionroles")
        print('-----------dump-----------')
        print(roles)
        print('--------------------------')
        print(self.bot.cache_reactionroles)
        print('-----------dump-----------')


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if await reaction_spam_check(self, payload):
            await process_reaction(self, payload, "add")




    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: RawReactionActionEvent):
        if await reaction_spam_check(self, payload):
            await process_reaction(self, payload, "remove")


    
    # @has_permissions(manage_guild=True)
    # @bot_has_permissions(add_reactions=True)
    # @commands.command()
    # async def rr(self, ctx):
    #     def check(message):
    #         return message.author == ctx.author and message.channel == ctx.channel

    #     await ctx.send('Mention the channel that the reaction roles message is in.')
    #     try:    
    #         msg = await self.bot.wait_for('message', check=check, timeout=30)
    #         if msg.channel_mentions:
    #             ch = msg.channel_mentions[0]
    #             CHANNEL = ch
    #             if ch.guild == ctx.guild:
    #                 pass
    #             else:
    #                 return await ctx.send('Channel is not in this guild/does not exist. Please restart the process.')
    #         else:
    #             return await ctx.send('I did not find any channel mentions in your message. Please restart the process.')

        
    #         await ctx.send('Send the ID for the message that you would like to use for reaction roles.') 
    #         msg = await self.bot.wait_for('message', check=check, timeout=30)
    #         if msg.content.isnumeric():
    #             pm = ch.get_partial_message(int(msg.content)) #discord.errors.NotFound
    #             PARTIALMSG = pm
    #             try:
    #                 pm.add_reaction('👀')
    #                 await asyncio.sleep(0.25)
    #                 pm.remove_reaction('👀')
    #             except discord.errors.NotFound:
    #                 return await ctx.send('Message ID is invalid. (ID does not belong to a message). Please restart the process.')
    #             except discord.errors.Forbidden:
    #                 return await ctx.send('I was not able to access this message or permissions are missing to add reactions to the message. Please restart the process.')
    #         else:
    #             return await ctx.send('Message ID is invalid. Please restart the process.')


    #         await ctx.send('How many reactions will be available for the user to choose from?')
    #         msg = await self.bot.wait_for('message', check=check, timeout=30)
    #         if msg.content.isnumeric():
    #             COUNT = int(msg)
    #         else:
    #             try:
    #                 return await ctx.reply('This must be a whole, positive and valid number!')
    #             except:
    #                 return

    #         cnt = COUNT
    #         while cnt < 0:
    #             cnt -= 1

    #             await ctx.send('Send one of the emojis.')
    #             msg = await self.bot.wait_for('message', check=check, timeout=30)


                



    #     except asyncio.exceptions.TimeoutError:
    #         return await ctx.send('Operation timed out. Please try again.')


        

            
def setup(bot):
    bot.add_cog(rr(bot))