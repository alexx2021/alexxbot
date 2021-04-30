import discord
from discord.ext import commands
import asyncio
import datetime
from utils.utils import get_or_fetch_channel, sendlog, check_if_log



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




class Invites(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = InviteTracker(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(2)
        #print('Starting to cache invites!')
        #print('--------------------------')
        await self.tracker.cache_invites()
        #print('--------------------------')
        #print('Finished caching invites!')
        print('Bot is ready!')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await asyncio.sleep(0.25)

        god = guild.owner.id
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetchrow("SELECT user_id FROM userblacklist WHERE user_id = $1", god) #checks if a user in BL owns the server
            if rows:
                await guild.leave()
                
                embed = discord.Embed(colour=0xe74c3c)
                embed.set_author(name=f"Left guild with blacklisted owner")
                embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
                "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
                "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
                "\n" + "Created at " + str(guild.created_at), inline=False)
                embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})')) 
                embed.set_thumbnail(url=guild.icon_url)
                
                chID = 813600852576829470
                ch = await get_or_fetch_channel(self, chID)
                await ch.send(embed=embed)
                
                return

        async with self.bot.db.acquire() as connection:
            rows = await connection.fetchrow("SELECT guild_id FROM guildblacklist WHERE guild_id = $1", guild.id)#checks if its a guild in the BL 
            if rows:
                await guild.leave()
                
                embed = discord.Embed(colour=0xe74c3c)
                embed.set_author(name=f"Left blacklisted guild")
                embed.add_field(name=(str(guild.name)), value=str(guild.id) + 
                "\n" + str(len(list(filter(lambda m: m.bot, guild.members)))) + " bots" + 
                "\n" + str(len(list(filter(lambda m: not m.bot, guild.members)))) + " humans" + 
                "\n" + "Created at " + str(guild.created_at), inline=False)
                embed.add_field(name='Server Owner', value=(f'{guild.owner} ({guild.owner.id})')) 
                embed.set_thumbnail(url=guild.icon_url)
                
                chID = 813600852576829470
                ch = await get_or_fetch_channel(self, chID)
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


        if await check_if_log(self, member.guild):
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

            
            await sendlog(self, member.guild, embed1)


    @commands.is_owner()
    @commands.command()
    async def dumpd(self, ctx):
       await self.tracker.dumpdict(ctx)
    


def setup(bot):
    bot.add_cog(Invites(bot))

