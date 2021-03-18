import discord
from discord.ext import commands
import asyncio
import datetime

async def get_or_fetch_channel(self, guild, channel_id):
        ch = guild.get_channel(channel_id)
        if ch is not None:
            return ch

        try:
            ch = await guild.fetch_channel(channel_id)
        except discord.HTTPException:
            return None
        else:
            return ch


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
        rows2 = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),)

        if rows2 != []:    
                
            gid = member.guild.id
            uid = member.id

            query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
            params = (gid, uid)
            rows = await self.bot.i.execute_fetchall(query, params)
            
            if rows != []:
                toprow = rows[0]
                invby = toprow[3]
                if invby != 4:
                    query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                    params = (gid, invby)
                    rows = await self.bot.i.execute_fetchall(query, params)
                    if rows != []:
                        toprow = rows[0]
                        invcount = toprow[2]
                        newinvcount = invcount - 1
                        query = 'UPDATE invites SET inv_count = ? WHERE guild_id = ? AND user_id = ?' 
                        params = (newinvcount, gid, invby)
                        await self.bot.i.execute(query, params)
                        await self.bot.i.commit()





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
        rows = await self.bot.bl.execute_fetchall("SELECT user_id FROM userblacklist WHERE user_id = ?",(god,),) #checks if a user in BL owns the server
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
            ch = self.bot.get_channel(813600852576829470)
            if not ch:
                ch = self.bot.fetch_channel(813600852576829470)
                print('fetched channel for guild bl msg')
            await ch.send(embed=embed)
            
            return

        
        rows = await self.bot.bl.execute_fetchall("SELECT guild_id FROM guildblacklist WHERE guild_id = ?",(guild.id,),)#checks if its a guild in the BL 
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
            ch = self.bot.get_channel(813600852576829470)
            if not ch:
                ch = self.bot.fetch_channel(813600852576829470)
                print('fetched channel for guild bl msg')
            await ch.send(embed=embed)
            
            return
        
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
        rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),)

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
                
                #does not need a logging entry check because under on_join it is already checked
                gid = member.guild.id
                uid = inviter.id
                

                query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                params = (gid, uid)
                rows = await self.bot.i.execute_fetchall(query, params)
                
                #inviter queries
                if rows != []:
                    toprow = rows[0]
                    invcount = toprow[2]
                    newinvcount = invcount + 1

                    query = 'UPDATE invites SET inv_count = ? WHERE guild_id = ? AND user_id = ?'
                    params = (newinvcount, gid, uid)
                    await self.bot.i.execute(query, params)
                    await self.bot.i.commit()

                else:
                    noinvhistory = 4
                    oneinv = 1
                    await self.bot.i.execute("INSERT INTO invites VALUES(?, ?, ?, ?)", (gid, uid, oneinv, noinvhistory))
                    await self.bot.i.commit()
                
                
                #member who got invited queries
                query = 'SELECT guild_id, user_id, inv_count, inv_by FROM invites WHERE guild_id = ? AND user_id = ?' 
                params = (gid, member.id)
                rows2 = await self.bot.i.execute_fetchall(query, params)
                
                if rows2 != []:

                    query = 'UPDATE invites SET inv_by = ? WHERE guild_id = ? AND user_id = ?' #update inv_by
                    params = (inviter.id, gid, member.id)
                    await self.bot.i.execute(query, params)
                    await self.bot.i.commit()

                else:
                    zeroinv = 0
                    await self.bot.i.execute("INSERT INTO invites VALUES(?, ?, ?, ?)", (gid, member.id, zeroinv, inviter.id))
                    await self.bot.i.commit()



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

            
            server = member.guild.id
            rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),)
            if rows != []:
                toprow = rows[0]
                chID = toprow[1]
                ch = await get_or_fetch_channel(self, member.guild, chID)
                try:
                    await ch.send(embed=embed1)
                except discord.errors.Forbidden:
                    await self.bot.sc.execute("DELETE FROM logging WHERE log_channel = ?",(ch.id,))
                    await self.bot.sc.commit()
                    print('deleted log channel b/c no perms to speak') 
    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpd(self, ctx):
       await self.tracker.dumpdict(ctx)
    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpinv(self, ctx):
        rows = await self.bot.i.execute_fetchall("SELECT * FROM invites")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')
    









def setup(bot):
    bot.add_cog(Invites(bot))

