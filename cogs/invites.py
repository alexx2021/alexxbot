import discord
from discord.ext import commands
import asyncio
import datetime


async def on_join_db_update(member, inviter):
    #### on join:
    # inviter is fetched
    # if it is NOT none
    # check db if user who made inv link exists by searching for the member.guild.id AND the inviter.id
    # 
    # if user does exist, add 1 to their count
    # else add them, and make their inv_count 1, and make their inv_by a special number, lets just say "4" cause thats a cool number 
    # (will symbolize an unknown for who was their original inviter)
    # 
    # if new member has an entry, update their inv_by
    # else add an entry and enter their inv by and set their inv_count to 0

    #invites(guild_id INTERGER, user_id INTERGER, inv_count INTERGER, inv_by INTERGER)
    


    async with aiosqlite.connect('invites.db') as c:
        #does not need a logging entry check because under on_join it is already checked
        gid = member.guild.id
        uid = inviter.id
        
        if inviter is None:
            return

        query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
        params = (gid, uid)
        rows = await c.execute_fetchall(query, params)
        
        #inviter queries
        if rows != []:
            toprow = rows[0]
            invcount = toprow[2]
            newinvcount = invcount + 1

            query = 'UPDATE invites SET inv_count = ? WHERE guild_id = ? AND user_id = ?'
            params = (newinvcount, gid, uid)
            await c.execute(query, params)
            await c.commit()

        else:
            noinvhistory = 4
            oneinv = 1
            await c.execute("INSERT INTO invites VALUES(?, ?, ?, ?)", (gid, uid, oneinv, noinvhistory))
            await c.commit()
        
        
        #member who got invited queries
        query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
        params = (gid, member.id)
        rows2 = await c.execute_fetchall(query, params)
        
        if rows2 != []:

            query = 'UPDATE invites SET inv_by = ? WHERE guild_id = ? AND user_id = ?' #update inv_by
            params = (inviter.id, gid, member.id)
            await c.execute(query, params)
            await c.commit()

        else:
            zeroinv = 0
            await c.execute("INSERT INTO invites VALUES(?, ?, ?, ?)", (gid, member.id, zeroinv, inviter.id))
            await c.commit()



#I am using this because I want the bot to check if it has proper permissions before attemping to cache invites. 
# going to replace the try/except discord forbidden with perm checks
# 
# these functions belong to the discordutils lib
#
class InviteTracker(object):
    def __init__(self, bot):
        self.bot = bot
        self._cache = {}
        
    async def cache_invites(self):
        for guild in self.bot.guilds:
            self._cache[guild.id] = {}
            if guild.me.guild_permissions.manage_guild: #added perms check
                #print(f'{guild} cached')
                invs = await guild.invites()
                for invite in invs:
                    if invite.inviter not in self._cache[guild.id].keys():
                        self._cache[guild.id][invite.inviter] = []
                    self._cache[guild.id][invite.inviter].append(invite)

        
    async def update_invite_cache(self, invite):
        if invite.guild.me.guild_permissions.manage_guild: #added perms check
            if not invite.guild.id in self._cache.keys():
                self._cache[invite.guild.id] = {}
            if not invite.inviter in self._cache[invite.guild.id].keys():
                self._cache[invite.guild.id][invite.inviter] = []
            self._cache[invite.guild.id][invite.inviter].append(invite)

    async def remove_invite_cache(self, invite):
        for key in self._cache:
            for lists in self._cache[key]:
                user = self._cache[key][lists]
                if invite in user:
                    self._cache[key][lists].remove(invite)
                    break
                    
    async def remove_guild_cache(self, guild):
        if guild.id in self._cache.keys():
            del self._cache[guild.id]
                
    async def update_guild_cache(self, guild):
        if guild.me.guild_permissions.manage_guild: #added perms check
            invs = await guild.invites()
            self._cache[guild.id] = {}
            for invite in invs:
                if not invite.inviter in self._cache[guild.id].keys():
                    self._cache[guild.id][invite.inviter] = []
                self._cache[guild.id][invite.inviter].append(invite)
        
    async def fetch_inviter(self, member):
        invited_by = None
        invs = {}
        if member.guild.me.guild_permissions.manage_guild: #added permission check
            new_invites = await member.guild.invites()
        else:
            return None

        for invite in new_invites:
            if not invite.inviter in invs.keys():
                invs[invite.inviter] = []
            invs[invite.inviter].append(invite)
        for new_invite_key in invs:
            for cached_invite_key in self._cache[member.guild.id]:
                if new_invite_key == cached_invite_key:
                    new_invite_list = invs[new_invite_key]
                    cached_invite_list = self._cache[member.guild.id][cached_invite_key]
                    for new_invite in new_invite_list:
                        for old_invite in cached_invite_list:
                            if new_invite.code == old_invite.code and new_invite.uses-old_invite.uses >= 1:
                                cached_invite_list.remove(old_invite)
                                cached_invite_list.append(new_invite)
                                return new_invite_key
    
    async def dumpdict(self, ctx):
        await ctx.send(self._cache)




class Invites(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = InviteTracker(bot)

        self.conn = sqlite3.connect('serverconfigs.db')
        self.c = self.conn.cursor()
        self.conn2 = sqlite3.connect('blacklists.db')
        self.c2 = self.conn2.cursor()

        self.conn3 = sqlite3.connect('invites.db')
        self.c3 = self.conn3.cursor()
        self.c3.execute("CREATE TABLE IF NOT EXISTS invites(guild_id INTERGER, user_id INTERGER, inv_count INTERGER, inv_by INTERGER)")
        self.c3.close()
        self.conn3.close() # I want to use aiosqlite so im creating the table on the main thread, and closing it so it doesnt interfere with the async stuff


    # invites per server
    # invites are subtracted if people leave
    #
    #
    #### on join:
    # inviter is fetched
    # if it is NOT none
    # check db if user who made inv link exists by searching for the member.guild.id AND the inviter.id
    # 
    # if user does exist, add 1 to their count
    # else add them, and make their inv_count 1, and make their inv_by a special number, lets just say "4" cause thats a cool number 
    # (will symbolize an unknown for who was their original inviter)
    # 
    # if new member has an entry, update their inv_by
    # else add an entry and enter their inv by and set their inv_count to 0
    # 
    #### on leave
    # check if member is in the db, and who invited them
    # if someone invited them, find the db entry for that person (guild id AND user id) and subtract the count
    #
    # possibly add a resetinvites command?
    #
    #
    # #DISABLE THIS IF THEY DONT HAVE AN INVITE LOGGING CHANNEL? 


    ##################################################### Invites db updates for leave
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        server = member.guild.id
        rows2 = self.c.execute("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),).fetchall()

        if rows2 != []:    
            async with aiosqlite.connect('invites.db') as c:
                
                gid = member.guild.id
                uid = member.id

                query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                params = (gid, uid)
                rows = await c.execute_fetchall(query, params)
                
                if rows != []:
                    toprow = rows[0]
                    invby = toprow[3]
                    if invby != 4:
                        query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                        params = (gid, invby)
                        rows = await c.execute_fetchall(query, params)
                        if rows != []:
                            toprow = rows[0]
                            invcount = toprow[2]
                            newinvcount = invcount - 1
                            query = 'UPDATE invites SET inv_count = ? WHERE guild_id = ? AND user_id = ?' 
                            params = (newinvcount, gid, invby)
                            await c.execute(query, params)
                            await c.commit()





            #on join functions are in the other on member join in this file LOL, I dont wanna ping the api twice to fetch the data

    


    ##################################################### Invite Caching and updating + log channel sending 
    # + check if guild is blacklisted on join (I bundled this function in here so the guild cache would not be updated if the server was blacklisted.)
    # (no point in making a guild blacklist check in a separate cog because it would have to query the db twice at once)
    #
    # the invites db update on join is also here

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        print('Starting to cache invites!')
        print('--------------------------')
        await self.tracker.cache_invites()
        print('--------------------------')
        print('Finished caching invites!')
        print('Bot is ready!')
        print(f"Servers - {str(len(self.bot.guilds))}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await asyncio.sleep(1)

        god = guild.owner.id
        rows = self.c2.execute("SELECT user_id FROM userblacklist WHERE user_id = ?",(god,),).fetchall() #checks if a user in BL owns the server
        if rows != []:
            await guild.leave()
            
            embed = discord.Embed(colour=0xe74c3c)
            embed.set_author(name=f"Left guild with blacklisted owner")
            embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
            "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
            "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
            "\n" + "Created at " + str(guild.created_at), inline=False)
            embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})')) 
            embed.set_thumbnail(url=guild.icon_url)
            await send_statsHook(embed)
            
            return

        
        rows = self.c2.execute("SELECT guild_id FROM guildblacklist WHERE guild_id = ?",(guild.id,),).fetchall() #checks if its a guild in the BL 
        if rows != []:
            await guild.leave()
            
            embed = discord.Embed(colour=0xe74c3c)
            embed.set_author(name=f"Left blacklisted guild")
            embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
            "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
            "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
            "\n" + "Created at " + str(guild.created_at), inline=False)
            embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})')) 
            embed.set_thumbnail(url=guild.icon_url)
            await send_statsHook(embed)
            
            return
        
        else:
            await self.tracker.update_guild_cache(guild) #finally does the updating if all is good

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        server = member.guild.id
        rows = self.c.execute("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),).fetchall()

        if rows != []:
            inviter = await self.tracker.fetch_inviter(member)  # inviter is the member who invited
            if inviter:
                created_at = member.created_at.strftime("%b %d, %Y")
                embed1 = discord.Embed(color=0x00FF00)
                embed1.set_author(name=f"{member}", icon_url=member.avatar_url)
                embed1.title = f"Member joined" 
                embed1.description = f'Account created on {created_at}'
                embed1.add_field(name='Inviter', value=f'{inviter}', inline = True)
                embed1.timestamp = datetime.datetime.utcnow()
                embed1.set_footer(text=f'ID: {member.id}' + '\u200b')               
                
                await on_join_db_update(member, inviter) #function that updates the invites db on join


            else:
                created_at = member.created_at.strftime("%b %d, %Y")
                embed1 = discord.Embed(color=0x00FF00)
                embed1.set_author(name=f"{member}", icon_url=member.avatar_url)
                embed1.title = f"Member joined" 
                embed1.description = f'Account created on {created_at}'
                embed1.add_field(name='Inviter', value=f'???', inline = True)
                embed1.add_field(name='Error', value=f'Bot does not have sufficient\n permissions to view invites \n or an error occurred', inline = True) #sometimes the inviter is none due to an error
                embed1.timestamp = datetime.datetime.utcnow()
                embed1.set_footer(text=f'ID: {member.id}' + '\u200b')

            

            toprow = rows[0] 
            whURL = toprow[2]
            await send_wh2(whURL, embed1, embed) #sends both embeds in one message
    
    @commands.command()
    async def dumpd(self, ctx):
       await self.tracker.dumpdict(ctx)
    









def setup(bot):
    bot.add_cog(Invites(bot))

