import logging
import discord
from discord.ext import commands
import datetime
import utils.musicUtils
import traceback
import sys
from discord.ext.commands.errors import CommandError, MaxConcurrencyReached
logger = logging.getLogger('discord')


class Errors(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot    


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, "original", error)
        # if isinstance(error, commands.CommandError):
        #     error = error.original

        if isinstance(error, commands.CommandNotFound):
            #await ctx.send('Invalid command used.')
            return
        
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'<a:x_:826577785173704754> Command is missing required arguments. Correct usage: `{ctx.command} {ctx.command.signature}`')
        
        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention}, You must wait **{round(error.retry_after, 2)}** seconds before using this command again.')
        
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(f"<a:x_:826577785173704754> {ctx.author.mention}, {error}.")

        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send(f" <a:x_:826577785173704754> {error}.")

        elif isinstance(error, commands.BadArgument):
            return await ctx.send(f'<a:x_:826577785173704754> Command was given bad/invalid arguments. `{error}`')
        
        elif isinstance(error, commands.NotOwner): 
            return

        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(f'<a:x_:826577785173704754> You cannot use this command in DMs!.')
        
        elif isinstance(error, MaxConcurrencyReached):
            return await ctx.send(f'<a:x_:826577785173704754> This command cannot be run at this time due to concurrency limits.')
            
        elif isinstance(error, commands.errors.NSFWChannelRequired):
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention}, {error}')
        
        ###################################################
        # the following are for the music portion of the bot
        
        
        elif isinstance(error, commands.errors.CheckFailure):
            return
        
        elif isinstance(error, utils.musicUtils.NotConnectedToVoice):
            return await ctx.send('<a:x_:826577785173704754> The bot is not currently in a voice channel! Join a voice channel and play a song and it will join.')


        elif isinstance(error, utils.musicUtils.NotPlaying):
            return await ctx.send('<a:x_:826577785173704754> There is no song currently playing!')

        elif isinstance(error, utils.musicUtils.EmptyQueue):
            return await ctx.send('<a:x_:826577785173704754> The queue is currently empty!')

        else:
            # embed = discord.Embed(title=':x: Command Error', colour=0xe74c3c) #Red
            # embed.add_field(name='Error', value=error)
            # embed.add_field(name='Who', value=f'{ctx.author} ({ctx.author.id})')
            # embed.add_field(name=f"Command:", value=f"{ctx.message.clean_content}")
            # embed.description = '```py\n%s\n```' % traceback.format_exc()
            # embed.timestamp = discord.utils.utcnow()
            # owner = self.bot.get_user(247932598599417866)
            # if not owner:
            #     owner = await self.bot.fetch_user(247932598599417866)
            # await owner.send(embed=embed)
            
            logger.warning(msg=f'COMMAND ERROR - {ctx.message.clean_content} - {error} - u.{ctx.author.id} g.{ctx.guild.id}')
            #All unhandled Errors will print their original traceback
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        
        # embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
        # embed.add_field(name='Event', value=event)
        # embed.description = '```py\n%s\n```' % traceback.format_exc()
        # embed.timestamp = discord.utils.utcnow()
        # owner = self.bot.get_user(247932598599417866)
        # if not owner:
        #     owner = await self.bot.fetch_user(247932598599417866)
       
        # await owner.send(embed=embed)
        logger.warning(msg=f'EVENT ERROR - {event} - {traceback.format_exc()}')
        
        print(f'{event}')
        print(f'{traceback.format_exc()}')

def setup(bot):
    bot.add_cog(Errors(bot))