import asyncio
import discord
import datetime
from discord.ext import commands
from discord.ext.commands import has_permissions
from discord.ext.commands import bot_has_permissions
from discord.ext.commands.cooldowns import BucketType
from utils.utils import get_or_fetch_member, sendlog

BOT_ID = int(752585938630082641)



#Moderation Category
class Moderation(commands.Cog):
    """🚨 Commands to help you keep your server safe"""
    def __init__(self, bot):
        self.bot = bot
        self._cd = commands.CooldownMapping.from_cooldown(5.0, 10.0, commands.BucketType.user)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True

    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            await asyncio.sleep(1)
            beforeR = [r.name for r in before.roles]
            afterR = [r.name for r in after.roles]
            if "alexxmuted" in beforeR:
                if not "alexxmuted" in afterR:
                    query = 'DELETE FROM pmuted_users WHERE guild_id = ? AND user_id = ?' # delete data from db only pertaining to the specific user and guild
                    gid = before.guild.id
                    uid = before.id
                    params = (gid, uid)
                    await self.bot.m.execute(query, params)
                    await self.bot.m.commit()

    #clear command
    @bot_has_permissions(manage_messages=True, read_message_history=True)    
    @commands.max_concurrency(1, per=BucketType.channel, wait=True)
    @has_permissions(manage_messages=True)
    @commands.command(aliases=["purge"], help="Clears messages. Messages older than 2 weeks cannot be deleted.")
    async def clear(self, ctx,*, limit:int):
        with ctx.channel.typing():
            if limit <= 0:
                return await ctx.send('Please choose a number that is not 0 or negative!')
            if limit >= 501:
                return await ctx.send('Maximum number is 500 messages!')
            deleted = await ctx.channel.purge(limit=limit + 1, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
            if (len(deleted)-1) > 0:
                await ctx.send(f'Deleted {(len(deleted)) - 1} messages! `:P`', delete_after=2.0)
            if (len(deleted)-1) == 0:
                await ctx.send('No messages were deleted. Are they older than 2 weeks?')
            # await ctx.channel.purge(limit=limit + 1, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
            # await ctx.send(f'Deleted {limit} messages! `:P`', delete_after=2.0)


    
    # Checks if there is a muted role on the server and creates one if there isn't
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_messages=True)
    @commands.command(help="Mutes a user until you unmute them.")
    async def mute(self, ctx, member: discord.Member,*, reason=None):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)
    
        if ctx.message.author.id == member.id: #checks to see if you are muting yourself
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot mute yourself, silly human! `>.<`')

        # if member.guild_permissions.manage_messages: #checks to see if you are muting someone who you probs shoudln't be able to mute
        #     return await ctx.send(f'{ctx.author.mention} you cannot mute someone who also has permission to mute people! `:C`')

        if member.top_role >= ctx.author.top_role:
            await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot mute someone who has an equal or higher role than you! `:C`')
            return
        
        if member.id == BOT_ID:
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot mute me with my own commands! `>.<`')
        
        role3 = discord.utils.get(member.guild.roles, name="alexxmuted")
        if role3:
            if role3 in member.roles:
                return await ctx.send('<a:x_:826577785173704754> User is already muted!')
            if member.guild.me.top_role.position <= role3.position:
                return await ctx.send('<a:x_:826577785173704754> Error. The alexxmuted role is above my highest role.')


        role2 = discord.utils.get(member.guild.roles, name="alexxmuted") # retrieves muted role returns none if there isn't 
        if not role2: # checks if there is muted role
            muted = await ctx.guild.create_role(name="alexxmuted", reason="To use for muting")
            
            successfulchannels = 0
            failedchannels = 0 
            for channel in ctx.guild.channels: # removes permission to view and send in the channels 

                channelperms = channel.permissions_for(ctx.guild.me)
                if channelperms.view_channel is False:
                    failedchannels += 1
                    pass 
                elif channelperms.manage_permissions is False:
                    failedchannels += 1
                    pass 
                else:
                    await channel.set_permissions(muted, send_messages=False,
                                                read_message_history=False,
                                                read_messages=False)
                    successfulchannels += 1
            await member.add_roles(muted, reason=f"By {ctx.author} for {reason}") # adds newly created muted role

            await self.bot.m.execute("INSERT INTO pmuted_users VALUES(?, ?)", (guild_id, user_id)) #adds user to db
            await self.bot.m.commit()

            await ctx.send(f"{member.mention} has been muted. <a:check:826577847023829032>")

            embedSummary = discord.Embed(color=0x7289da)
            embedSummary.title = f"Channel permissions setup summary" 
            embedSummary.description='(For the muted role)'
            embedSummary.add_field(name='Success', value=f'{successfulchannels} channels')
            embedSummary.add_field(name='Failure', value=f'{failedchannels} channels')
            embedSummary.add_field(name='Possible reasons for failure', value='1. I cannot view the channel\n 2. I cannot manage permissions in the channel')
            embedSummary.timestamp = datetime.datetime.utcnow()
            await ctx.send(embed=embedSummary)
            

            embed = discord.Embed(color=0x979c9f)
            embed.title = f"{member} muted" 
            embed.description = f'**Staff member:** {ctx.author.mention} \n**Reason:** {reason}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar_url) 
            embed.set_footer(text=f'ID: {member.id}' + '\u200b')

            await sendlog(self, ctx.guild, embed)
     

        else:
            await member.add_roles(role2, reason=f"By {ctx.author} for {reason}") # adds already existing muted role

            await self.bot.m.execute("INSERT INTO pmuted_users VALUES(?, ?)", (guild_id, user_id)) #adds user to db
            await self.bot.m.commit()
            
            await ctx.send(f"{member.mention} has been muted. <a:check:826577847023829032>") #0x979c9f
            
            embed = discord.Embed(color=0x979c9f)
            embed.title = f"{member} muted" 
            embed.description = f'**Staff member:** {ctx.author.mention} \n**Reason:** {reason}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar_url) 
            embed.set_footer(text=f'ID: {member.id}' + '\u200b')

            await sendlog(self, ctx.guild, embed)

    
    # @commands.command(hidden=True)
    # @commands.is_owner()
    # async def gchp(self, ctx):
    #     await ctx.send(f'{ctx.channel.permissions_for(ctx.guild.me)}')
    #     channelperms = ctx.channel.permissions_for(ctx.guild.me)
    #     await ctx.send(f'{channelperms.view_channel}')

    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpM(self, ctx):
        rows = await self.bot.m.execute_fetchall("SELECT guild_id, user_id FROM pmuted_users")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')
            

    
    #unmutes a user
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_messages=True)
    @commands.command(help='Unmutes a user.')
    async def unmute(self, ctx, member: discord.Member,*, reason=None):
        
        role = discord.utils.get(member.guild.roles, name="alexxmuted")
        if role:
            if member.guild.me.top_role.position <= role.position:
                return await ctx.send('<a:x_:826577785173704754> Error. The alexxmuted role is above my highest role.')

            if role in member.roles:
                await member.remove_roles(discord.utils.get(member.guild.roles, name="alexxmuted")) # removes muted role

                gid = str(ctx.guild.id)
                uid = str(member.id)

                query = 'DELETE FROM pmuted_users WHERE guild_id = ? AND user_id = ?' # delete data from db only pertaining to the specific user and guild
                params = (gid, uid)
                await self.bot.m.execute(query, params)
                await self.bot.m.commit()

                await ctx.send(f"{member.mention} has been unmuted. <a:check:826577847023829032>")

                embed = discord.Embed(color=0x979c9f)
                embed.title = f"{member} unmuted" 
                embed.description = f'**Staff member:** {ctx.author.mention} \n**Reason:** {reason}'
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_thumbnail(url=member.avatar_url) 
                embed.set_footer(text=f'ID: {member.id}' + '\u200b')

                await sendlog(self, ctx.guild, embed)    	

            else:
                return await ctx.send('<a:x_:826577785173704754> User is not muted!')
        else:
            return await ctx.send('<a:x_:826577785173704754> No muted role has been created for this server! Mute someone to create one.')


    #event to check if the user is still muted upon joining a server
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await asyncio.sleep(0.25)
        

        gid = str(member.guild.id)
        uid = str(member.id)

        query = 'SELECT guild_id, user_id FROM pmuted_users WHERE guild_id = ? AND user_id = ?' # delete data from db only pertaining to the specific user and guild
        params = (gid, uid)
        rows = await self.bot.m.execute_fetchall(query, params)

        if rows != []:
            toprow = rows[0]
            user_id = toprow[1]
            
            if member.id == user_id:
                role = discord.utils.get(member.guild.roles, name="alexxmuted") # checks if there is a muted role 
                if role: # checks if there is muted role
                    if member.guild.me.guild_permissions.manage_roles: # checks if the bot has enough permissions to add the role
                        if member.guild.me.top_role.position > role.position:
                            await member.add_roles(role, reason=f"Left while muted.") # adds already existing muted role




			
                
    
    #bans a user
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)        
    @commands.command(help='Bans a user.')
    async def ban(self, ctx, user: discord.User,*, reason=None):
        if ctx.message.author.id == user.id: #checks to see if you are banning yourself
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot ban yourself, silly human! `>.<`')
        
        member = await get_or_fetch_member(self, ctx.guild, user.id)
        if member:
            if member.top_role >= ctx.author.top_role:
                await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot ban someone who has an equal or higher role than you! `:C`')
                return
            if member.guild.me.top_role <= member.top_role:
                return await ctx.send('<a:x_:826577785173704754> Error. The user you are trying to ban is above my highest role.')
        
        if user.id == BOT_ID:
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot ban me with my own commands! SMH.')

        try:
            await ctx.guild.ban(user, reason=f"By {ctx.author} for {reason}")
            await ctx.send(f'{user.mention} was banned! `>:(` <a:check:826577847023829032>')
				

            embed = discord.Embed(color=0x546e7a)
            embed.title = f"{user} banned" 
            embed.description = f'**Staff member:** {ctx.author.mention} \n**Reason:** {reason}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=user.avatar_url) 
            embed.set_footer(text=f'ID: {user.id}' + '\u200b') 
            
            await sendlog(self, ctx.guild, embed)      

        except:
            return await ctx.send("<a:x_:826577785173704754> Could not ban this user.")

            
    #bans a user
    @bot_has_permissions(kick_members=True)
    @has_permissions(kick_members=True)        
    @commands.command(help='Kicks a user.')
    async def kick(self, ctx, member: discord.Member,*, reason=None):
        if ctx.message.author.id == member.id: #checks to see if you are kick yourself
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot kick yourself, silly human! `>.<`')
        
        if member.top_role >= ctx.author.top_role:
            await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot kick someone who has an equal or higher role than you! `:C`')
            return
        
        if member.id == BOT_ID:
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot kick me with my own commands! SMH.')
        
        if member.guild.me.top_role <= member.top_role:
            return await ctx.send('<a:x_:826577785173704754> Error. The user you are trying to kick is above my highest role.')

        try:
            await ctx.guild.kick(member, reason=f"By {ctx.author} for {reason}")
            await ctx.send(f'{member.mention} was kicked! `>:(` <a:check:826577847023829032>')
				

            embed = discord.Embed(color=0x546e7a)
            embed.title = f"{member} kicked" 
            embed.description = f'**Staff member:** {ctx.author.mention} \n**Reason:** {reason}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=member.avatar_url) 
            embed.set_footer(text=f'ID: {member.id}' + '\u200b') 
            
            await sendlog(self, ctx.guild, embed)   

        except:
            return await ctx.send("<a:x_:826577785173704754> Could not kick this user.")
        # try:
        #     await member.send(f'You were kicked from **{member.guild}** for "{reason}"')
        # except discord.errors.Forbidden:
        #     print(f'dm upon kick failed - Guild: {member.guild} ({member.guild.id})')  

    
    #softbans a user
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True)        
    @commands.command(help='Softbans a user.')
    async def softban(self, ctx, user: discord.User,*, reason=None):
        if ctx.message.author.id == user.id: #checks to see if you are banning yourself
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot softban yourself, silly human! `>.<`')

        member = await get_or_fetch_member(self, ctx.guild, user.id)
        if member:
            if member.top_role >= ctx.author.top_role:
                await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot softban someone who has an equal or higher role than you! `:C`')
                return
            if member.guild.me.top_role <= member.top_role:
                return await ctx.send('<a:x_:826577785173704754> Error. The user you are trying to softban is above my highest role.')
        
        if user.id == BOT_ID:
            return await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention} you cannot softban me with my own commands! SMH.')

        try:
            await ctx.guild.ban(user, reason=f"By {ctx.author} for {reason}")
            await ctx.guild.unban(user)
            await ctx.send(f'{user.mention} was softbanned! `>:(` <a:check:826577847023829032>')
				
            embed = discord.Embed(color=0x546e7a)
            embed.title = f"{user} softbanned" 
            embed.description = f'**Staff member:** {ctx.author.mention} \n**Reason:** {reason}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=user.avatar_url) 
            embed.set_footer(text=f'ID: {user.id}' + '\u200b') 
            
            await sendlog(self, ctx.guild, embed)
        except:
            return await ctx.send("<a:x_:826577785173704754> Could not softban this user.")
        
        # if member:
        #     try:
        #         await member.send(f'You were kicked from **{member.guild}** for "{reason}"')
        #     except discord.errors.Forbidden:
        #         print(f'dm upon kick failed - Guild: {member.guild} ({member.guild.id})')  



    #unbans a user by ID
    @bot_has_permissions(ban_members=True)
    @has_permissions(ban_members=True) 
    @commands.command(help='Unbans a user by ID.')
    async def unban(self, ctx, user: discord.User):
        try:
            await ctx.guild.unban(user)
            await ctx.send(f'{user} was unbanned! <a:check:826577847023829032>')

            embed = discord.Embed(color=0x546e7a)
            embed.title = f"{user} unbanned" 
            embed.description = f'**Staff member:** {ctx.author.mention}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_thumbnail(url=user.avatar_url) 
            embed.set_footer(text=f'ID: {user.id}' + '\u200b') 
            
            await sendlog(self, ctx.guild, embed)     


        except:
            return await ctx.send('<a:x_:826577785173704754> Could not unban this user.')


    #sets slowmode in a channel
    @bot_has_permissions(manage_channels=True)
    @has_permissions(manage_messages=True)
    @commands.command(aliases=["sm"], help="Sets the slowmode, in seconds.")
    async def slowmode(self, ctx, seconds: int):
        if seconds > 21600:
            return await ctx.send(f"<a:x_:826577785173704754> You tried to set the slowmode to **{seconds}** seconds, but the maximum is **21600** seconds")

        if seconds > 0:
            await ctx.send(f"Set the slowmode in this channel to **{seconds}** seconds! <a:check:826577847023829032>")
        else:
            seconds = 0
            await ctx.send(f'Disabled slowmode! <a:check:826577847023829032>')
        await ctx.channel.edit(slowmode_delay=seconds)

    @commands.group(help='Use this command to do specialized cleanup in a channel based on what type of content it is.')
    async def remove(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('<a:x_:826577785173704754> Invalid subcommand. Options: `bot`, `attachments`, `contains`.') #msg.attachments

    @remove.command(help='Removes messages that were sent by a bot. Only checks the last 100 messages in the channel.')
    @commands.max_concurrency(1, per=BucketType.channel, wait=True)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def bot(self, ctx):
        def is_bot(m):
            return m.author.bot
        with ctx.channel.typing():
            deleted = await ctx.channel.purge(limit=100, check=is_bot, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
            await ctx.send(f'Deleted {(len(deleted))} messages belonging to bots! `:P`', delete_after=3.0)

    @remove.command(help='Removes messages that are attachments. Only checks the last 100 messages in the channel.')
    @commands.max_concurrency(1, per=BucketType.channel, wait=True)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def attachments(self, ctx):
        def is_att(m):
            return m.attachments
        with ctx.channel.typing():
            deleted = await ctx.channel.purge(limit=100, check=is_att, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
            await ctx.send(f'Deleted {(len(deleted))} messages with attachments! `:P`', delete_after=3.0)
            
    @remove.command(help='Removes messages that contain text you input. Only checks the last 100 messages in the channel.')
    @commands.max_concurrency(1, per=BucketType.channel, wait=True)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def contains(self, ctx, *, string: str):
        if len(string) > 150:
            return await ctx.send('<a:x_:826577785173704754> Text is too long.')
        def m_contains(m):
            return string in m.content
        with ctx.channel.typing():
            deleted = await ctx.channel.purge(limit=100, check=m_contains, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
            await ctx.send(f'Deleted {(len(deleted))} messages containing **{string}**! `:P`', delete_after=3.0)
    
    #test

    @remove.command(help='Removes messages that were sent by the specified user. Only checks the last 100 messages in the channel.')
    @commands.max_concurrency(1, per=BucketType.channel, wait=True)
    @has_permissions(manage_messages=True)
    @bot_has_permissions(manage_messages=True, read_message_history=True)
    async def user(self, ctx, user: discord.User):
        def is_user(m):
            return m.author == user
        with ctx.channel.typing():
            deleted = await ctx.channel.purge(limit=100, check=is_user, after=datetime.datetime.utcnow() - datetime.timedelta(days=13))
            await ctx.send(f'Deleted {(len(deleted))} messages belonging to {user}! `:P`', delete_after=3.0)

def setup(bot):
    bot.add_cog(Moderation(bot))
