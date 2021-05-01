from discord.ext import commands



class migrate(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def migrate(self, ctx):
        counter = 0
        rows = await self.bot.xp.execute_fetchall('SELECT * FROM xp')
        await ctx.send('Fetched Rows! (1)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                user = int(row[1])
                xpamt = int(row[2])
                await connection.execute('INSERT INTO xp VALUES($1, $2, $3)', guild, user, xpamt)
                counter +=1

        await ctx.send(f'{counter} rows migrated to xp.')
        
        counter = 0
        rows = await self.bot.sc.execute_fetchall('SELECT * FROM logging')
        await ctx.send('Fetched Rows! (2)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                ch = int(row[1])
                await connection.execute('INSERT INTO logging VALUES($1, $2)', guild, ch)
                counter +=1

        await ctx.send(f'{counter} rows migrated to logging.')


        counter = 0
        rows = await self.bot.sc.execute_fetchall('SELECT * FROM welcome')
        await ctx.send('Fetched Rows! (3)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                ch = int(row[1])
                wmsg = str(row[2])
                bmsg = str(row[3])
                await connection.execute('INSERT INTO welcome VALUES($1, $2, $3, $4)', guild, ch, wmsg, bmsg)
                counter +=1

        await ctx.send(f'{counter} rows migrated to welcome.')


        counter = 0
        rows = await self.bot.sc.execute_fetchall('SELECT * FROM autogames')
        await ctx.send('Fetched Rows! (4)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                ch = int(row[1])
                delay = int(row[2])
                await connection.execute('INSERT INTO autogames VALUES($1, $2, $3)', guild, ch, delay)
                counter +=1

        await ctx.send(f'{counter} rows migrated to autogames.')

        counter = 0
        rows = await self.bot.sc.execute_fetchall('SELECT * FROM autorole')
        await ctx.send('Fetched Rows! (5)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                role = int(row[1])
                await connection.execute('INSERT INTO autorole VALUES($1, $2)', guild, role)
                counter +=1

        await ctx.send(f'{counter} rows migrated to autorole.')

        counter = 0
        rows = await self.bot.xp.execute_fetchall('SELECT * FROM chatlvlsenabled')
        await ctx.send('Fetched Rows! (6)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                enabled = str(row[1])
                await connection.execute('INSERT INTO xp_enabled VALUES($1, $2)', guild, enabled)
                counter +=1
        await ctx.send(f'{counter} rows migrated to chatlvlsenabled.')

        counter = 0
        rows = await self.bot.xp.execute_fetchall('SELECT * FROM lvlsenabled')
        await ctx.send('Fetched Rows! (7)')
        async with self.bot.db.acquire() as connection:
            for row in rows:
                guild = int(row[0])
                enabled = str(row[1])
                await connection.execute('INSERT INTO xp_lvlup VALUES($1, $2)', guild, enabled)
                counter +=1

        await ctx.send(f'{counter} rows migrated to lvlsenabled.')

def setup(bot):
    bot.add_cog(migrate(bot))