import asyncio
import aiohttp
from discord.ext import commands
import discord
import json
from discord.ext.commands.cooldowns import BucketType
from lxml import etree
from discord.ext.buttons import Paginator
from utils.utils import is_wl

class Pag(Paginator):
    async def teardown(self):
        try:
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

class CodeBlock:
    missing_error = 'Missing code block. Please use the following markdown\n\\`\\`\\`language\ncode here\n\\`\\`\\`'
    def __init__(self, argument):
        try:
            block, code = argument.split('\n', 1)
        except ValueError:
            raise commands.BadArgument(self.missing_error)

        if not block.startswith('```') and not code.endswith('```'):
            raise commands.BadArgument(self.missing_error)

        language = block[3:]
        self.command = self.get_command_from_language(language.lower())
        self.source = code.rstrip('`').replace('```', '')

    def get_command_from_language(self, language):
        cmds = {
            'cpp': 'g++ -std=c++17 -O2 -Wall -Wextra -pedantic -pthread main.cpp -lstdc++fs && ./a.out',
            'c': 'mv main.cpp main.c && gcc -std=c11 -O2 -Wall -Wextra -pedantic main.c && ./a.out',
            'py': 'python3 main.cpp',
            'python': 'python3 main.cpp',
            'haskell': 'runhaskell main.cpp'
        }

        cpp = cmds['cpp']
        for alias in ('cc', 'h', 'c++', 'h++', 'hpp'):
            cmds[alias] = cpp
        try:
            return cmds[language]
        except KeyError as e:
            if language:
                fmt = f'Unknown language to compile for: {language}'
            else:
                fmt = 'Could not find a language to compile with.'
            raise commands.BadArgument(fmt) from e


class Cplusplus(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.check(is_wl)
    @commands.max_concurrency(1, per=BucketType.user, wait=False)
    @commands.cooldown(2, 10, commands.BucketType.user)
    @commands.command()
    async def run(self, ctx, *, code: CodeBlock):
        """Compiles code via Coliru.
        You have to pass in a code block with the language syntax
        either set to one of these:
        - cpp
        - c
        - python
        - py
        - haskell
        Anything else isn't supported. The C++ compiler uses g++ -std=c++17.
        Please don't spam this for Stacked's sake.
        """
        payload = {
            'cmd': code.command,
            'src': code.source
        }

        data = json.dumps(payload)

        async with ctx.typing():
            async with aiohttp.ClientSession() as cs:
                async with cs.post('http://coliru.stacked-crooked.com/compile', data=data) as resp:
                    if resp.status != 200:
                        await ctx.send('Coliru did not respond in time.')
                        return

                    output = await resp.text(encoding='utf-8')

                    # if len(output) < 1980:
                    #     await ctx.send(f'```\n{output}\n```\n> Run by {ctx.author}')
                    #     return

                    if len(output) == 0:
                        return await ctx.send('There is no output for this query.')

                    pager = Pag(
                    title=f"Code output for {ctx.author}", 
                    colour=0,
                    timeout=10,
                    entries=[output[i: i + 2000] for i in range(0, len(output), 2000)],
                    length=1,
                    prefix="```\n",
                    suffix="\n```"
                )

                    await pager.start(ctx)
                    # # output is too big so post it in gist
                    # async with aiohttp.ClientSession() as cs:
                    #     async with cs.post('http://coliru.stacked-crooked.com/share', data=data) as r:
                    #         if r.status != 200:
                    #             await ctx.send('Could not create coliru shared link')
                    #         else:
                    #             shared_id = await r.text()
                    #             await ctx.send(f'Output too big. Coliru link: http://coliru.stacked-crooked.com/a/{shared_id}')

    @run.error
    async def run_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(error)
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(CodeBlock.missing_error)

    @commands.cooldown(4, 10, commands.BucketType.user)
    @commands.command()
    async def cpp(self, ctx, *, query: str):
        """Search something on cppreference"""

        url = 'https://en.cppreference.com/mwiki/index.php'
        params = {
            'title': 'Special:Search',
            'search': query
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers, params=params) as resp:
                if resp.status != 200:
                    return await ctx.send(f'<a:x_:826577785173704754> An error occurred (status code: {resp.status}). Retry later.')

                if resp.url.path != '/mwiki/index.php':
                    return await ctx.send(f'<{resp.url}>')

                e = discord.Embed()
                root = etree.fromstring(await resp.text(), etree.HTMLParser())

                nodes = root.findall(".//div[@class='mw-search-result-heading']/a")

                description = []
                special_pages = []
                for node in nodes:
                    href = node.attrib['href']
                    if not href.startswith('/w/cpp'):
                        continue

                    if href.startswith(('/w/cpp/language', '/w/cpp/concept')):
                        # special page
                        special_pages.append(f'[{node.text}](http://en.cppreference.com{href})')
                    else:
                        description.append(f'[`{node.text}`](http://en.cppreference.com{href})')

                if len(special_pages) > 0:
                    e.add_field(name='Language Results', value='\n'.join(special_pages), inline=False)
                    if len(description):
                        e.add_field(name='Library Results', value='\n'.join(description[:10]), inline=False)
                else:
                    if not len(description):
                        return await ctx.send('No results found.')

                    e.title = 'Search Results'
                    e.description = '\n'.join(description[:15])

                e.add_field(name='See More', value=f'[`{discord.utils.escape_markdown(query)}` results]({resp.url})')
                await ctx.send(embed=e)
    
def setup(bot):
	bot.add_cog(Cplusplus(bot))