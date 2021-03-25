import discord
import datetime
from discord.ext import commands
from utils import check_if_log, sendlog


    
class Logging(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    


    @commands.is_owner()
    @commands.command(hidden=True)
    async def dumpL(self, ctx):
        rows = await self.bot.sc.execute_fetchall("SELECT server_id, log_channel, whURL FROM logging")
        print('-----------dump-----------')
        print(rows)
        print('-----------dump-----------')
        print(self.bot.logcache)
        print('-----------dump-----------')
        
        await ctx.channel.send('done.')




    #message deletion logger
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return

        if await check_if_log(self, message.guild):
                
            if(message.author.bot):
                return

            #ignore channel for logging if it has "alexxlogsignore" in its topic
            topic = message.channel.topic
            if topic is not None:
                if 'alexxlogsignore' in topic:
                    return

            
            if message.attachments:
                attachment = message.attachments[0]

                e = discord.Embed(color=0xffa500)
                e.set_author(name=f"{message.author}", icon_url=message.author.avatar_url)
                e.title = f"Message deleted in #{message.channel.name}" 
                e.description = f'{message.content}'
                e.add_field(name='Attachments', value=f'{attachment.proxy_url}')
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f'ID: {message.author.id}' + '\u200b')


            else:
                e = discord.Embed(color=0xffa500)
                e.set_author(name=f"{message.author}", icon_url=message.author.avatar_url)
                e.title = f"Message deleted in #{message.channel.name}" 
                e.description = f'{message.content}'
                e.timestamp = datetime.datetime.utcnow()
                e.set_footer(text=f'ID: {message.author.id}' + '\u200b')

            await sendlog(self, message.guild, e)
        

    #message edit logger
    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if not message_before.guild:
            return

        if await check_if_log(self, message_before.guild):

            #ignore channel for logging if it has "alexxlogsignore" in its topic
            topic = message_before.channel.topic
            if topic is not None:
                if 'alexxlogsignore' in topic:
                    return
            

            #removes some spam
            if message_before.author == self.bot.user:
                return
            if(message_before.author.bot):
                return

            #does not log a message that was just pinned
            if message_after.pinned:
                return

            #does not log embeds(like in links)
            if message_after.embeds:
                return
            
            #if message is too long
            if len(message_before.content) + len(message_after.content) > 2000:
                return
            
            embed = discord.Embed(color=0x3498db)
            embed.set_author(name=f"{message_before.author}", icon_url=message_before.author.avatar_url)
            embed.title = f"Message edited in #{message_before.channel.name}"
            embed.description = f'**Before:** {message_before.content} \n+**After: ** {message_after.content}'
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f'ID: {message_before.author.id}' + '\u200b')

            await sendlog(self, message_before.guild, embed) 


     #currently moved to invites.py so that I can send this embed and the invite one in the same webhook send   

    # #attempt at a join message in logs
    # @commands.Cog.listener()
    # async def on_member_join(self, member):
		
    #     created_at = member.created_at.strftime("%b %d, %Y")

    #     embed = discord.Embed(color=0x00FF00)
    #     embed.set_author(name=f"{member}", icon_url=member.avatar_url)
    #     embed.title = f"Member joined" 
    #     embed.description = f'Account created on {created_at}'
    #     embed.timestamp = datetime.datetime.utcnow()
    #     embed.set_footer(text=f'ID: {member.id}' + '\u200b')
        
    #     server = member.guild.id
    #     rows = self.c.execute("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),).fetchall()
    #     if rows != []:
    #         toprow = rows[0] 
    #         whURL = toprow[2]
    #         await send_wh(whURL, embed)


    #attempt at a leave message in logs
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        
        if await check_if_log(self, member.guild):
            if member == self.bot.user:
                return
            
            embed = discord.Embed(color=0xff0000)
            embed.set_author(name=f"{member}", icon_url=member.avatar_url)
            embed.title = f"Member left" 
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=f'ID: {member.id}' + '\u200b')

            await sendlog(self, member.guild, embed)

    # user updates - 0x9b59b6 is the color for all
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            guilds = self.bot.guilds
            for guild in guilds: # I would prefer another method but this is the best I can do right now
                if guild.get_member(before.id):
                    if await check_if_log(self, guild):
                        embed = discord.Embed(color=0x9b59b6)
                        embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar_url)
                        embed.title = f"Username changed"
                        embed.description = f'**Before:** {before.name} \n+**After: ** {after.name}'
                        embed.timestamp = datetime.datetime.utcnow()
                        embed.set_footer(text=f'ID: {before.id}' + '\u200b')

                        await sendlog(self, guild, embed)

        # elif before.avatar_url != after.avatar_url:
        #     guilds = self.bot.guilds
        #     for guild in guilds:
        #         if guild.get_member(before.id):
        #             embed = discord.Embed(color=0x9b59b6)
        #             embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar_url)
        #             embed.title = f"Avatar changed"
        #             embed.description = f'**New avatar: **'
        #             embed.set_thumbnail(url=after.avatar_url)
        #             embed.timestamp = datetime.datetime.utcnow()
        #             embed.set_footer(text=f'ID: {before.id}' + '\u200b')

        #             server = guild.id
        #             rows = self.c.execute("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),).fetchall()
        #             if rows != []:
        #                 toprow = rows[0] 
        #                 whURL = toprow[2]
        #                 await send_wh(whURL, embed)
    
    #member updates
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if await check_if_log(self, before.guild):            
            if before == self.bot.user:
                return
            
            if before.display_name != after.display_name:

                embed = discord.Embed(color=0x9b59b6)
                embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar_url)
                embed.title = f"Nickname changed"
                embed.description = f'**Before:** {before.display_name} \n+**After: ** {after.display_name}'
                embed.timestamp = datetime.datetime.utcnow()
                embed.set_footer(text=f'ID: {before.id}' + '\u200b')
                
                await sendlog(self, before.guild, embed)

#         elif before.roles != after.roles:
            
#             guild = before.guild
            
#             embed = discord.Embed(title="Roles changed", colour=0x71368a, timestamp=datetime.datetime.utcnow()) #role changes have a darker purple hehe
#             embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.avatar_url)
#             embed.set_footer(text=f'ID: {before.id}' + '\u200b')
            
#             beforeR = [r.mention for r in before.roles]
#             afterR = [r.mention for r in after.roles]
#             del beforeR[0]
#             del afterR[0]

#             if beforeR == []:
#                 beforeR = ['None']
#             if afterR == []:
#                 afterR = ['None']


#             fields = [("Before", ", ".join(beforeR), False),
#                         ("After", ", ".join(afterR), False)]

#             for name, value, inline in fields:
#                 embed.add_field(name=name, value=value, inline=inline)

#             server = guild.id
#             rows = self.c.execute("SELECT server_id, log_channel, whURL FROM logging WHERE server_id = ?",(server,),).fetchall()
#             if rows != []:
#                 toprow = rows[0] 
#                 whURL = toprow[2]
#                 await send_wh(whURL, embed)
    

def setup(bot):
	bot.add_cog(Logging(bot))
