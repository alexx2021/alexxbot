import io
import discord
import datetime
from discord.ext import commands
from utils.utils import check_if_log, sendlog, sendlogFile


    
class Logging(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, bot):
        self.bot = bot    


    @commands.is_owner()
    @commands.command()
    async def dumpL(self, ctx):
        async with self.bot.db.acquire() as connection:
            rows = await connection.fetch("SELECT * FROM logging")
            print('-----------dump-----------')
            print(rows)
            print('-----------dump-----------')
            print(self.bot.cache_logs)
            print('-----------dump-----------')
            
            await ctx.channel.send('done.')




    #message deletion logger
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
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
                e.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)
                e.title = f"Message deleted in #{message.channel.name}" 
                e.description = f'{message.content}'
                e.add_field(name='Attachments', value=f'{attachment.proxy_url}')
                e.timestamp = discord.utils.utcnow()
                e.set_footer(text=f'ID: {message.author.id}' + '\u200b')


            else:
                e = discord.Embed(color=0xffa500)
                e.set_author(name=f"{message.author}", icon_url=message.author.display_avatar.url)
                e.title = f"Message deleted in #{message.channel.name}" 
                e.description = f'{message.content}'
                e.timestamp = discord.utils.utcnow()
                e.set_footer(text=f'ID: {message.author.id}' + '\u200b')

            await sendlog(self, message.guild, e)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):

        #ignore channel for logging if it has "alexxlogsignore" in its topic
        topic = messages[0].channel.topic
        if topic is not None:
            if 'alexxlogsignore' in topic:
                return


        msg = messages[0]
        if await check_if_log(self, msg.guild):
            buffer = io.BytesIO()
            theContent = ''
            for message in messages:
                theContent += f'{message.author} ({message.author.id}): {message.content}\n'
            buffer = io.BytesIO(theContent.encode("utf8"))
            
            e = discord.Embed(color=0xffa500, title=f'{len(messages)} messages purged in #{messages[0].channel.name}')
            e.timestamp = discord.utils.utcnow()
            await sendlog(self, message.guild, e)
            
            file = discord.File(fp=buffer, filename=f"{message.guild.id}-{message.channel.id}.txt")
            await sendlogFile(self, message.guild, file)
            buffer.close()
            


        

    #message edit logger
    @commands.Cog.listener()
    async def on_message_edit(self, message_before: discord.Message, message_after: discord.Message):
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
            
            
            embed = discord.Embed(color=0x3498db)
            embed.set_author(name=f"{message_before.author}", icon_url=message_before.author.display_avatar.url)
            embed.title = f"Message edited in #{message_before.channel.name}"
            embed.description = f'[Jump to the message]({message_after.jump_url})'
            
            if not message_before.content:
                embed.add_field(name='Before',value='...', inline=False)
            else:
                if len(message_before.content) > 1023:
                    embed.add_field(name='Before',value=f'{message_before.content[:1020] + "..."}', inline=False)
                else:
                    embed.add_field(name='Before',value=f'{message_before.content}', inline=False)

            if not message_after.content:
                embed.add_field(name='After',value='...', inline=False)
            else:
                if len(message_after.content) > 1023:
                    embed.add_field(name='After',value=f'{message_after.content[:1020] + "..."}', inline=False)
                else:
                    embed.add_field(name='After',value=f'{message_after.content}', inline=False)
                

            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f'ID: {message_before.author.id}' + '\u200b')

            await sendlog(self, message_before.guild, embed) 



    #attempt at a join message in logs
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if await check_if_log(self, member.guild):
            if member == self.bot.user:
                return

            created_at = member.created_at.strftime("%b %d, %Y")

            embed1 = discord.Embed(color=0x00FF00)
            embed1.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            embed1.title = f"Member joined" 
            embed1.description = f'Account created on {created_at}'
            embed1.timestamp = discord.utils.utcnow()
            embed1.set_footer(text=f'ID: {member.id}' + '\u200b')  

            await sendlog(self, member.guild, embed1)      


    #attempt at a leave message in logs
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        
        if await check_if_log(self, member.guild):
            if member == self.bot.user:
                return
            
            embed = discord.Embed(color=0xff0000)
            embed.set_author(name=f"{member}", icon_url=member.display_avatar.url)
            embed.title = f"Member left" 
            embed.timestamp = discord.utils.utcnow()
            embed.set_footer(text=f'ID: {member.id}' + '\u200b')

            await sendlog(self, member.guild, embed)

    # user updates - 0x9b59b6 is the color for all
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            for guild in before.mutual_guilds:
                if await check_if_log(self, guild):
                    embed = discord.Embed(color=0x9b59b6)
                    embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.display_avatar.url)
                    embed.title = f"Username changed"
                    embed.description = f'**Before:** {before.name} \n+**After: ** {after.name}'
                    embed.timestamp = discord.utils.utcnow()
                    embed.set_footer(text=f'ID: {before.id}' + '\u200b')

                    await sendlog(self, guild, embed)

        # elif before.display_avatar.url != after.display_avatar.url:
        #     guilds = self.bot.guilds
        #     for guild in guilds:
        #         if guild.get_member(before.id):
        #             embed = discord.Embed(color=0x9b59b6)
        #             embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.display_avatar.url)
        #             embed.title = f"Avatar changed"
        #             embed.description = f'**New avatar: **'
        #             embed.set_thumbnail(url=after.display_avatar.url)
        #             embed.timestamp = discord.utils.utcnow()
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
                embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.display_avatar.url)
                embed.title = f"Nickname changed"
                embed.description = f'**Before:** {before.display_name} \n+**After: ** {after.display_name}'
                embed.timestamp = discord.utils.utcnow()
                embed.set_footer(text=f'ID: {before.id}' + '\u200b')
                
                await sendlog(self, before.guild, embed)

#         elif before.roles != after.roles:
            
#             guild = before.guild
            
#             embed = discord.Embed(title="Roles changed", colour=0x71368a, timestamp=discord.utils.utcnow()) #role changes have a darker purple hehe
#             embed.set_author(name=f"{before.name}#{before.discriminator}", icon_url=before.display_avatar.url)
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
