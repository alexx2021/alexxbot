    # @discord.utils.cached_property
    # def webhook(self):
    #     hook = Webhook.from_url(os.getenv('SWH'), adapter=AsyncWebhookAdapter(self.bot.session))
    #     return hook

import discord
from discord.ext import commands
import datetime
import DiscordUtils
import traceback
import sys
from discord.ext.commands.errors import MaxConcurrencyReached
from discord.ext.commands.errors import NSFWChannelRequired


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    


    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            #await ctx.send('Invalid command used.')
            return
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Command is missing required arguments.')
        
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'{ctx.author.mention}, That command is on cooldown for another **{round(error.retry_after, 2)}** seconds')
            
            msg = ctx.message.clean_content
            if len(msg) >= 1023:
                channel = self.bot.get_channel(813600852576829470)
                await channel.send(f'**{ctx.author} ({ctx.author.id}) used a command with over 1024 chars. hmmm. blacklist them maybe?** :thinking:')
                return

            if ctx.message.guild:
                embed = discord.Embed(
                title=f"Command used. (triggered cooldown)",
                colour=0
                )
                embed.add_field(name=f"Where:", value=f"{ctx.guild.name} \n{ctx.guild.id}")
                embed.add_field(name=f"Who:", value=f"{ctx.author} \n{ctx.author.id}")
                embed.add_field(name=f"Command:", value=f"{msg}")
                embed.timestamp = datetime.datetime.utcnow()
                # embed.set_thumbnail(url=ctx.guild.icon_url)
                ch = self.bot.get_channel(813600852576829470)
                if not ch:
                    ch = self.bot.fetch_channel(813600852576829470)
                await ch.send(embed=embed)
            else:
                embed = discord.Embed(
                title=f"Command used. (triggered cooldown)",
                colour=0
                )
                embed.add_field(name=f"Where:", value=f"Private message")
                embed.add_field(name=f"Who:", value=f"{ctx.author} \n{ctx.author.id}")
                embed.add_field(name=f"Command:", value=f"{msg}")
                embed.timestamp = datetime.datetime.utcnow()
                #embed.set_thumbnail(url=ctx.guild.icon_url)
                ch = self.bot.get_channel(813600852576829470)
                if not ch:
                    ch = self.bot.fetch_channel(813600852576829470)
                await ch.send(embed=embed)
        
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, You are missing the following permissions: `{' '.join(error.missing_perms)}`.")

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"I am missing the following permissions: `{' '.join(error.missing_perms)}`.")

        elif isinstance(error, commands.BadArgument):
            await ctx.send(f'Command was given bad arguments.')
        
        elif isinstance(error, commands.NotOwner): 
            return

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(f'You cannot use this command in DMs!.')
        
        elif isinstance(error, MaxConcurrencyReached):
            await ctx.send(f'This command cannot be run while there is a another instance currently running in this channel.')
            
        elif isinstance(error, commands.errors.NSFWChannelRequired):
            await ctx.send(f'{ctx.author.mention} This command cannot be run in a non-nsfw marked channel...')
        
        ###################################################
        # the following are for the music portion of the bot
        
        
        elif isinstance(error, commands.errors.CheckFailure):
            return
        
        elif isinstance(error, DiscordUtils.NotConnectedToVoice):
            await ctx.send('The bot is not currently in a voice channel! Join a voice channel and play a song and it will join.')


        elif isinstance(error, DiscordUtils.NotPlaying):
            await ctx.send('There is no song currently playing!')

        elif isinstance(error, DiscordUtils.EmptyQueue):
            await ctx.send('The queue is currently empty!')

        else:
            embed = discord.Embed(title=':x: Command Error', colour=0xe74c3c) #Red
            embed.add_field(name='Command', value=error)
            embed.add_field(name='Who', value=f'{ctx.author} ({ctx.author.id})')
            embed.add_field(name=f"Command:", value=f"{ctx.message.clean_content}")
            embed.description = '```py\n%s\n```' % traceback.format_exc()
            embed.timestamp = datetime.datetime.utcnow()
            owner = self.bot.get_user(247932598599417866)
            if not owner:
                owner = await self.bot.fetch_user(247932598599417866)
            await owner.send(embed=embed)
            
            #All unhandled Errors will print their original traceback
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
        embed.add_field(name='Event', value=event)
        embed.description = '```py\n%s\n```' % traceback.format_exc()
        embed.timestamp = datetime.datetime.utcnow()
        owner = self.bot.get_user(247932598599417866)
        if not owner:
            owner = await self.bot.fetch_user(247932598599417866)
        await owner.send(embed=embed)
        print(f'{event}')
        print(f'{traceback.format_exc()}')

def setup(bot):
    bot.add_cog(Errors(bot))