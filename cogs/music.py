import asyncio
import discord
from discord.ext import commands
from discord.ext.commands.core import bot_has_permissions
import utils.musicUtils
import datetime
from discord.ext.buttons import Paginator


class Pag(Paginator):
    async def teardown(self):
        try:
            await asyncio.sleep(0.25)
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass



async def is_wl(ctx):
    guildlist = [
    741054230370189343,
    812951618945286185,
    704554442153787453,
    783345613860372480,
    812520226603794432,
    597965043333726220,
    796212175693152256,
    828536119628267540,
    ]
    #iridescent
     #alexx support
      #sniper kingdom
       #burrow's resource pack
        #minty
         #server
          #math pre cal 1
            #my newest class server
    guildID = ctx.guild.id
    if guildID in guildlist:
        return True 
    else:
        return False
    
async def not_pl(ctx):
    await ctx.send('<a:x_:826577785173704754> There is nothing currently playing :(')

async def convertT(songDur):
    conversion = datetime.timedelta(seconds=songDur)
    converted_time = str(conversion)
    return converted_time

async def check_in_vc(ctx):
    if ctx.guild.me.voice:
        vc = ctx.guild.me.voice.channel
    else:
        vc = None

    # If we've connected to a voice chat and we're in the same voice channel
    if not vc or (ctx.author.voice and vc == ctx.author.voice.channel):
        return True
    else:
        await ctx.send(f'<a:x_:826577785173704754> {ctx.author.mention}, you must be in the same voice channel as me to use this command!')
        return False



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.music = utils.musicUtils.Music() 
        self._cd = commands.CooldownMapping.from_cooldown(4.0, 10.0, commands.BucketType.user)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
        else:
            return True


    @commands.is_owner()
    @commands.command(hidden=True)
    async def dcall(self, ctx):
        for guild in self.bot.guilds:
            player = self.music.get_player(guild_id=guild.id)
            if player:
                await player.stop()
                await ctx.send(f':ok_hand: {guild} ({guild.id}) stopped!')
                asyncio.sleep(0.5)

    @commands.check(check_in_vc) 
    @commands.check(is_wl)    
    @commands.command(aliases=["l"],hidden=True)
    async def leave(self, ctx):
        
        if ctx.author.voice:
            player = self.music.get_player(guild_id=ctx.guild.id)
            if player:
                await player.stop()
            await ctx.voice_client.disconnect()
        
    
    @commands.check(check_in_vc)
    @commands.check(is_wl)    
    @commands.command(aliases=["p"],hidden=True)
    async def play(self, ctx, *, songname):
        

        if ctx.voice_client:
            if not ctx.author.voice:
                await ctx.send(embed=f'<a:x_:826577785173704754> You must be in a voice channel to use this command!')
                return
        if ctx.voice_client is None: #joins vc if its not already in one
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                
                chperms = channel.permissions_for(ctx.guild.me)
                if not chperms.connect:
                    return await ctx.send('<a:x_:826577785173704754> I cannot connect to that channel. (missing permissions)')
                if not chperms.speak:
                    return await ctx.send('<a:x_:826577785173704754> I cannot speak in that channel. (missing permissions)')

                await ctx.author.voice.channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

        if "mau5" in songname:
            await ctx.send(f'{ctx.author.mention} deadmau5 is cool - i approve')
        if "http:" in songname:
            return await ctx.send('<a:x_:826577785173704754> URLs are not supported at this time as the music module is still in development.')




        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            
            try:
                await player.queue(songname, search=True)
            except IndexError:
                return await ctx.send('<a:x_:826577785173704754> No songs found.')

            song = await player.play()
            
            converted_time = await convertT(song.duration)

            embed = discord.Embed(color=0x7289da)
            embed.title = "Now playing:"
            embed.description = (f'{song.name} `{converted_time}`')
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            song = await player.queue(songname, search=True)

            converted_time = await convertT(song.duration)
            
            embed = discord.Embed(color=0x7289da)
            embed.title = "Queued:"
            embed.description = (f'{song.name} `{converted_time}`')
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.check(check_in_vc)
    @commands.check(is_wl)      
    @commands.command(hidden=True)
    async def pause(self, ctx):
        

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song = await player.pause()
        embed = discord.Embed(description=(f'Paused **{song.name}**.'), color=0x7289da)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(check_in_vc)
    @commands.check(is_wl)      
    @commands.command(hidden=True)
    async def resume(self, ctx):
        

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song = await player.resume()
        embed = discord.Embed(description=(f'Resumed playing **{song.name}**.'), color=0x7289da)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(check_in_vc)
    @commands.check(is_wl)       
    @commands.command(hidden=True)
    async def stop(self, ctx):
        

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        await player.stop()
        embed = discord.Embed(description=(f'Stopped playing audio.'), color=0x7289da)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(check_in_vc)
    @commands.check(is_wl)        
    @commands.command(hidden=True)
    async def loop(self, ctx):
        

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song = await player.toggle_song_loop()
        if song.is_looping:
            embed = discord.Embed(description=(f'Enabled loop for **{song.name}**'), color=0x7289da)
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=(f'Disabled loop for **{song.name}**'), color=0x7289da)
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.check(is_wl) 
    @bot_has_permissions(manage_messages=True)    
    @commands.command(aliases=["q"],hidden=True)
    async def queue(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
            

        if len([song.name for song in player.current_queue()]) > 0:
            embed = discord.Embed(title=(f'Queue'), color=0x7289da)
            embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
            desc = ''
            for rank, song in enumerate(player.current_queue(), start=1):
                converted_time = await convertT(song.duration)
                
                desc +=f'**{rank}.** '+ song.name + f' `{converted_time}`\n'
        
            

            pager = Pag(
                title=f"Queue", 
                colour=0x7289da,
                timeout=10,
                entries=[desc[i: i + 2000] for i in range(0, len(desc), 2000)],
                length=1,
                suffix=f'\nRequested by {ctx.author}'
            )
            await pager.start(ctx)
        else:
            await ctx.send('<a:x_:826577785173704754> There is nothing in the queue.')


    @commands.check(is_wl)      
    @commands.command(aliases=["nowplaying"],hidden=True)
    async def np(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        
        song = player.now_playing()
        if not song:
            await not_pl(ctx)
            return

        
        converted_time = await convertT(song.duration)

        embed = discord.Embed(color=0x7289da)
        embed.title = "Now playing:"
        embed.description = (f'{song.name} `{converted_time}`')
        embed.add_field(name='Song link', value=(f'[Click here]({song.url})'), inline = True)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl)
    @commands.cooldown(2, 10, commands.BucketType.user)    
    @commands.command(help='If you would like to save a song you hear playing, do this command and you will be DMed the link!',aliases=["favorite"],hidden=True)
    async def save(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        
        song = player.now_playing()
        if not song:
            await not_pl(ctx)
            return

        await ctx.send(f'Saved **{song.name}**!')
        user = ctx.author
        
        embed = discord.Embed(color=0x7289da)
        embed.title = "Song you asked me to save :)"
        embed.description = (f'{song.name}')
        embed.add_field(name='Song link', value=(f'[Click here]({song.url})'), inline = True)
        try:    
            await user.send(embed=embed)
        except discord.errors.Forbidden:
            pass
        
    @commands.check(check_in_vc)
    @commands.check(is_wl)     
    @commands.command(hidden=True)                                                                                                                     #### TODO FIX ####
    async def skip(self, ctx):
        

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        data = await player.skip(force=True)
        
        embed = discord.Embed(description=(f'Skipped **{data[0].name}**'), color=0x7289da)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(check_in_vc)
    @commands.check(is_wl) 
    @commands.command(aliases=["vol"],hidden=True)
    async def volume(self, ctx, vol:int ):
        

        if vol > 200:
            await ctx.channel.send('<a:x_:826577785173704754> Volume cannot be greater than 200%!')
            return

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song, volume = await player.change_volume(float(vol / 100))
        embed = discord.Embed(description=(f"Changed volume for **{song.name}** to `{volume*100}%`"), color=0x7289da)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(check_in_vc)
    @commands.check(is_wl)     
    @commands.command(hidden=True)
    async def remove(self, ctx, index: int):
        

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
            
        index = index - 1
        if index < 0:
            return await ctx.send('<a:x_:826577785173704754> The song you tried to remove does not exist!')
        try:
            song = await player.remove_from_queue(int(index))
        except IndexError:
            await ctx.send('<a:x_:826577785173704754> The song you tried to remove does not exist!')
            return

        embed = discord.Embed(description=(f'Removed **{song.name}** from the queue.'), color=0x7289da)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)





def setup(bot):
	bot.add_cog(Music(bot))