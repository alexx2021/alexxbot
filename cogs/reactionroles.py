import asyncio
from utils.utils import get_or_fetch_guild, get_or_fetch_member
import discord
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions, command, has_permissions
from discord.raw_models import RawReactionActionEvent
import re

async def is_def_emoji(self, ctx, emoji):
    reStr = "('?:\U0001f1e6[\U0001f1e8-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f2\U0001f1f4\U0001f1f6-\U0001f1fa\U0001f1fc\U0001f1fd\U0001f1ff])|(?:\U0001f1e7[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ef\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1fe\U0001f1ff])|(?:\U0001f1e8[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ee\U0001f1f0-\U0001f1f5\U0001f1f7\U0001f1fa-\U0001f1ff])|(?:\U0001f1e9[\U0001f1ea\U0001f1ec\U0001f1ef\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1ff])|(?:\U0001f1ea[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ed\U0001f1f7-\U0001f1fa])|(?:\U0001f1eb[\U0001f1ee-\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1f7])|(?:\U0001f1ec[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ee\U0001f1f1-\U0001f1f3\U0001f1f5-\U0001f1fa\U0001f1fc\U0001f1fe])|(?:\U0001f1ed[\U0001f1f0\U0001f1f2\U0001f1f3\U0001f1f7\U0001f1f9\U0001f1fa])|(?:\U0001f1ee[\U0001f1e8-\U0001f1ea\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9])|(?:\U0001f1ef[\U0001f1ea\U0001f1f2\U0001f1f4\U0001f1f5])|(?:\U0001f1f0[\U0001f1ea\U0001f1ec-\U0001f1ee\U0001f1f2\U0001f1f3\U0001f1f5\U0001f1f7\U0001f1fc\U0001f1fe\U0001f1ff])|(?:\U0001f1f1[\U0001f1e6-\U0001f1e8\U0001f1ee\U0001f1f0\U0001f1f7-\U0001f1fb\U0001f1fe])|(?:\U0001f1f2[\U0001f1e6\U0001f1e8-\U0001f1ed\U0001f1f0-\U0001f1ff])|(?:\U0001f1f3[\U0001f1e6\U0001f1e8\U0001f1ea-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f4\U0001f1f5\U0001f1f7\U0001f1fa\U0001f1ff])|\U0001f1f4\U0001f1f2|(?:\U0001f1f4[\U0001f1f2])|(?:\U0001f1f5[\U0001f1e6\U0001f1ea-\U0001f1ed\U0001f1f0-\U0001f1f3\U0001f1f7-\U0001f1f9\U0001f1fc\U0001f1fe])|\U0001f1f6\U0001f1e6|(?:\U0001f1f6[\U0001f1e6])|(?:\U0001f1f7[\U0001f1ea\U0001f1f4\U0001f1f8\U0001f1fa\U0001f1fc])|(?:\U0001f1f8[\U0001f1e6-\U0001f1ea\U0001f1ec-\U0001f1f4\U0001f1f7-\U0001f1f9\U0001f1fb\U0001f1fd-\U0001f1ff])|(?:\U0001f1f9[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ed\U0001f1ef-\U0001f1f4\U0001f1f7\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1ff])|(?:\U0001f1fa[\U0001f1e6\U0001f1ec\U0001f1f2\U0001f1f8\U0001f1fe\U0001f1ff])|(?:\U0001f1fb[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ee\U0001f1f3\U0001f1fa])|(?:\U0001f1fc[\U0001f1eb\U0001f1f8])|\U0001f1fd\U0001f1f0|(?:\U0001f1fd[\U0001f1f0])|(?:\U0001f1fe[\U0001f1ea\U0001f1f9])|(?:\U0001f1ff[\U0001f1e6\U0001f1f2\U0001f1fc])|(?:\U0001f3f3\ufe0f\u200d\U0001f308)|(?:\U0001f441\u200d\U0001f5e8)|(?:[\U0001f468\U0001f469]\u200d\u2764\ufe0f\u200d(?:\U0001f48b\u200d)?[\U0001f468\U0001f469])|(?:(?:(?:\U0001f468\u200d[\U0001f468\U0001f469])|(?:\U0001f469\u200d\U0001f469))(?:(?:\u200d\U0001f467(?:\u200d[\U0001f467\U0001f466])?)|(?:\u200d\U0001f466\u200d\U0001f466)))|(?:(?:(?:\U0001f468\u200d\U0001f468)|(?:\U0001f469\u200d\U0001f469))\u200d\U0001f466)|[\u2194-\u2199]|[\u23e9-\u23f3]|[\u23f8-\u23fa]|[\u25fb-\u25fe]|[\u2600-\u2604]|[\u2638-\u263a]|[\u2648-\u2653]|[\u2692-\u2694]|[\u26f0-\u26f5]|[\u26f7-\u26fa]|[\u2708-\u270d]|[\u2753-\u2755]|[\u2795-\u2797]|[\u2b05-\u2b07]|[\U0001f191-\U0001f19a]|[\U0001f1e6-\U0001f1ff]|[\U0001f232-\U0001f23a]|[\U0001f300-\U0001f321]|[\U0001f324-\U0001f393]|[\U0001f399-\U0001f39b]|[\U0001f39e-\U0001f3f0]|[\U0001f3f3-\U0001f3f5]|[\U0001f3f7-\U0001f3fa]|[\U0001f400-\U0001f4fd]|[\U0001f4ff-\U0001f53d]|[\U0001f549-\U0001f54e]|[\U0001f550-\U0001f567]|[\U0001f573-\U0001f57a]|[\U0001f58a-\U0001f58d]|[\U0001f5c2-\U0001f5c4]|[\U0001f5d1-\U0001f5d3]|[\U0001f5dc-\U0001f5de]|[\U0001f5fa-\U0001f64f]|[\U0001f680-\U0001f6c5]|[\U0001f6cb-\U0001f6d2]|[\U0001f6e0-\U0001f6e5]|[\U0001f6f3-\U0001f6f6]|[\U0001f910-\U0001f91e]|[\U0001f920-\U0001f927]|[\U0001f933-\U0001f93a]|[\U0001f93c-\U0001f93e]|[\U0001f940-\U0001f945]|[\U0001f947-\U0001f94b]|[\U0001f950-\U0001f95e]|[\U0001f980-\U0001f991]|\u00a9|\u00ae|\u203c|\u2049|\u2122|\u2139|\u21a9|\u21aa|\u231a|\u231b|\u2328|\u23cf|\u24c2|\u25aa|\u25ab|\u25b6|\u25c0|\u260e|\u2611|\u2614|\u2615|\u2618|\u261d|\u2620|\u2622|\u2623|\u2626|\u262a|\u262e|\u262f|\u2660|\u2663|\u2665|\u2666|\u2668|\u267b|\u267f|\u2696|\u2697|\u2699|\u269b|\u269c|\u26a0|\u26a1|\u26aa|\u26ab|\u26b0|\u26b1|\u26bd|\u26be|\u26c4|\u26c5|\u26c8|\u26ce|\u26cf|\u26d1|\u26d3|\u26d4|\u26e9|\u26ea|\u26fd|\u2702|\u2705|\u270f|\u2712|\u2714|\u2716|\u271d|\u2721|\u2728|\u2733|\u2734|\u2744|\u2747|\u274c|\u274e|\u2757|\u2763|\u2764|\u27a1|\u27b0|\u27bf|\u2934|\u2935|\u2b1b|\u2b1c|\u2b50|\u2b55|\u3030|\u303d|\u3297|\u3299|\U0001f004|\U0001f0cf|\U0001f170|\U0001f171|\U0001f17e|\U0001f17f|\U0001f18e|\U0001f201|\U0001f202|\U0001f21a|\U0001f22f|\U0001f250|\U0001f251|\U0001f396|\U0001f397|\U0001f56f|\U0001f570|\U0001f587|\U0001f590|\U0001f595|\U0001f596|\U0001f5a4|\U0001f5a5|\U0001f5a8|\U0001f5b1|\U0001f5b2|\U0001f5bc|\U0001f5e1|\U0001f5e3|\U0001f5e8|\U0001f5ef|\U0001f5f3|\U0001f6e9|\U0001f6eb|\U0001f6ec|\U0001f6f0|\U0001f930|\U0001f9c0|[#|0-9]\u20e3"

    thing = re.findall(reStr, emoji)
    return thing

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


    @commands.group(help='Use this to manage reaction role settings.')
    async def rr(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `set`, `remove`, `clear`.')

    @has_permissions(manage_guild=True)
    @bot_has_permissions(add_reactions=True, manage_roles=True)
    @rr.command(help='Remove an emoji from your reaction role message.')
    async def remove(self, ctx, channelMention: discord.TextChannel, msgID: int, emoji: str):
        if await is_def_emoji(self, ctx, emoji) == []:
            return await ctx.send('<a:x_:826577785173704754> Only default discord emojis are allowed to be used.')

        if channelMention.guild == ctx.guild:
            pass
        else:
            return await ctx.send('<a:x_:826577785173704754> Channel is not in this guild.')

        p_msg = channelMention.get_partial_message(int(msgID))
        try:
            await p_msg.clear_reaction(emoji)
        except:
            return await ctx.send('<a:x_:826577785173704754> An error occured.\n\nPossible reasons why this failed: \n1. I was not able to access this message \n2. Permissions are missing to remove reactions from the message \n3. The message ID you provided is not valid')
        
        try:
            self.bot.cache_reactionroles[ctx.guild.id][msgID].pop(str(emoji))
        except KeyError:
            async with self.bot.db.acquire() as connection:
                await connection.execute('DELETE FROM reactionroles WHERE guild_id = $1 AND message_id = $2 AND reaction = $3', ctx.guild.id, msgID, emoji)
            return await ctx.send('<a:x_:826577785173704754> You cannot remove this emoji because there is no role associated with it.')

        async with self.bot.db.acquire() as connection:
            await connection.execute('DELETE FROM reactionroles WHERE guild_id = $1 AND message_id = $2 AND reaction = $3', ctx.guild.id, msgID, emoji)


    @has_permissions(manage_guild=True)
    @bot_has_permissions(add_reactions=True, manage_roles=True)
    @rr.command(help='Associate a reaction on a message with a role to be given.')
    async def set(self, ctx, channelMention: discord.TextChannel, msgID: int, emoji: str, role: discord.Role):
        if await is_def_emoji(self, ctx, emoji) == []:
            return await ctx.send('<a:x_:826577785173704754> Only default discord emojis are allowed to be used.')
        
        
        if channelMention.guild == ctx.guild:
            pass
        else:
            return await ctx.send('<a:x_:826577785173704754> Channel is not in this guild.')

        p_msg = channelMention.get_partial_message(int(msgID))
        try:
            await p_msg.add_reaction(emoji)
        except:
            return await ctx.send('<a:x_:826577785173704754> An error occured.\n\nPossible reasons why this failed: \n1. I was not able to access this message \n2. Permissions are missing to add reactions to the message \n3. The message ID you provided is not valid')

        if ctx.author.top_role.position <= role.position:
            return await ctx.send('<a:x_:826577785173704754> The role you chose is above your highest role.')
        if ctx.guild.me.top_role.position <= role.position:
            return await ctx.send('<a:x_:826577785173704754> The role you chose is above my highest role.')
    

        try:
            self.bot.cache_reactionroles[ctx.guild.id]
        except KeyError:
            self.bot.cache_reactionroles[ctx.guild.id] = {msgID: {str(emoji): role.id} }

        try:
            self.bot.cache_reactionroles[ctx.guild.id][msgID][str(emoji)] = role.id
        except KeyError:
            self.bot.cache_reactionroles[ctx.guild.id][msgID] = {str(emoji): role.id}

        async with self.bot.db.acquire() as connection:
            await connection.execute('DELETE FROM reactionroles WHERE guild_id = $1 AND message_id = $2 AND reaction = $3', ctx.guild.id, msgID, emoji)
            await connection.execute('INSERT INTO reactionroles VALUES ($1, $2, $3, $4)', ctx.guild.id, msgID, emoji, role.id)


        e = discord.Embed(description=f'[Jump to message]({p_msg.jump_url})', color= 0)


        await ctx.send(content =f'<a:check:826577847023829032> The emoji {str(emoji)} has been associated with the role {role.mention}', embed=e)


    
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
