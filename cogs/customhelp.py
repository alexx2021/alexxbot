
import discord
from discord.ext import commands

bot_title = 'Alexx-bot help'
bottom_info = '[Documentation](http://alexx.lol) | [Support Server](https://discord.gg/zPWMRMXQ7H) | [Invite Me!](https://discord.com/api/oauth2/authorize?client_id=752585938630082641&permissions=2080763127&scope=bot)'
prefix = ''

async def generate_command_list(self, cog):
    """ Generates the command list with properly spaced help messages """
    # Determine longest word
    max = 0
    for command in self.bot.get_cog(cog).get_commands():
        if not command.hidden:
            if len(f'{command}') > max:
                max = len(f'{command}')
    # Build list
    temp = ""
    for command in self.bot.get_cog(cog).get_commands():
        if command.hidden:
            temp += ''
        elif command.help is None:
            temp += f'{command}\n'
        else:
            temp += f'`{command}`'
            for i in range(0, max - len(f'{command}') + 1):
                temp += '   '
            temp += f'{command.help}\n'
    return temp
async def generate_usage(self, command_name):
    """ Generates a string of how to use a command """
    temp = f'{prefix}'
    command = self.bot.get_command(command_name)
    # Aliases
    if len(command.aliases) == 0:
        temp += f'{command_name}'
    elif len(command.aliases) == 1:
        temp += f'[{command.name}|{command.aliases[0]}]'
    else:
        t = '|'.join(command.aliases)
        temp += f'[{command.name}|{t}]'
    # Parameters
    params = f' '
    for param in command.clean_params:
        params += f'<{command.clean_params[param]}> '
    temp += f'{params}'
    return temp


class Help(commands.Cog):
    """ Help commands """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
                      description='Help command',
                      aliases=['commands', 'invite'])
    async def help(self, ctx, *commands: str):
        """ Shows this message """
        embed = discord.Embed(title=bot_title, description=f'Mention me to get my prefix on this server!')

        # Help by itself just lists our own commands.
        if len(commands) == 0:
            for cog in self.bot.cogs:
                temp = await generate_command_list(self, cog)
                if temp != "":
                    embed.add_field(name=f'**{cog}**', value=temp, inline=False)
            if bottom_info != "":
                embed.add_field(name="Links", value=bottom_info, inline=False)
        elif len(commands) == 1:
            # Try to see if it is a cog name
            name = commands[0].capitalize()
            command = None

            if name in self.bot.cogs:
                cog = self.bot.get_cog(name)
                msg = await generate_command_list(self, name)
                embed.add_field(name=name, value=msg, inline=False)
                msg = f'{cog.description}\n'
                embed.set_footer(text=msg)

            # Must be a command then
            else:
                command = self.bot.get_command(name)
                if command is not None:
                    help = f''
                    if command.help is not None:
                        help = command.help
                    embed.add_field(name=f'**{command}**',
                                    value=f'{command.description}```{await generate_usage(self, name)}```\n{help}',
                                    inline=False)
                else:
                    msg = ' '.join(commands)
                    embed.add_field(name="Not found", value=f'Command/category `{msg}` not found.')
        else:
            msg = ' '.join(commands)
            embed.add_field(name="Not found", value=f'Command/category `{msg}` not found.')

        await ctx.send(f'{ctx.author.mention}', embed=embed)
        return


# Cog setup
def setup(bot):
    bot.add_cog(Help(bot))