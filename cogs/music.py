import discord
from discord.ext import commands
import DiscordUtils
import datetime




async def is_wl(ctx):
    guildlist = [
    814039730026840094,
    741054230370189343,
    812951618945286185,
    704554442153787453,
    783345613860372480,
    812520226603794432,
    597965043333726220,
    ]
    #0b kits
     #iridescent
      #alexx support
       #sniper kingdom
        #burrow's resource pack
         #minty
          #server
    guildID = ctx.guild.id
    if guildID in guildlist:
        return True 
    else:
        return False
    
async def not_pl(ctx):
    embed = discord.Embed(description=('There is nothing currently playing :('), color=0xff0000)
    await ctx.send(embed=embed)

async def convertT(songDur):
    conversion = datetime.timedelta(seconds=songDur)
    converted_time = str(conversion)
    return converted_time

async def check_in_vc(ctx):
    # if ctx.voice_ c l i e n t:
    #     if not ctx.author.voice:
    #         embed = discord.Embed(description=(f'{ctx.author}, you must be in a voice channel to use this command!'), color=0xff0000)
    #         await ctx.send(embed=embed)
    #         return
        pass



class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.music = DiscordUtils.Music() 

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
            player = self.music.get_player(guild_id=member.guild.id)
            if not player:
                mg = member.guild
                if mg.voice_client:
                    await mg.voice_client.disconnect()


    # @commands.check(is_wl)
    # @commands.command(aliases=["j"])
    # async def join(self, ctx):
    #     if ctx.voice_client:
    #         if not ctx.author.voice:
    #             embed = discord.Embed(description=(f'{ctx.author.mention}, you must be in a voice channel to use this command!'), color=0xff0000)
    #             await ctx.send(embed=embed)
    #             return
    #     if ctx.voice_client is None: #joins vc if its not already in one
    #         if ctx.author.voice:
    #             channel = ctx.author.voice
    #             await ctx.author.voice.channel.connect()
    #             await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

    
    @commands.check(is_wl)    
    @commands.command(aliases=["l"])
    async def leave(self, ctx):
        if ctx.author.voice:
            player = self.music.get_player(guild_id=ctx.guild.id)
            if player:
                await player.stop()
            await ctx.voice_client.disconnect()
        else:
            embed = discord.Embed(description=(f'{ctx.author.mention}, you must be in a voice channel to use this command!'), color=0xff0000)
            await ctx.send(embed=embed)
        
    

    @commands.check(is_wl)    
    @commands.command(aliases=["p"])
    async def play(self, ctx, *, url):
        
        if ctx.voice_client:
            if not ctx.author.voice:
                embed = discord.Embed(description=(f'{ctx.author.mention}, you must be in a voice channel to use this command!'), color=0xff0000)
                await ctx.send(embed=embed)
                return
        if ctx.voice_client is None: #joins vc if its not already in one
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await ctx.author.voice.channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)

        if "mau5" in url:
            await ctx.send(f'{ctx.author.mention} deadmau5 is cool - i approve')




        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            
            try:
                await player.queue(url, search=True)
            except IndexError:
                return await ctx.send('No songs found.')

            song = await player.play()
            
            converted_time = await convertT(song.duration)

            embed = discord.Embed(color=0x7289da)
            embed.title = "Now playing:"
            embed.description = (f'{song.name} `{converted_time}`')
            embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            song = await player.queue(url, search=True)

            converted_time = await convertT(song.duration)
            
            embed = discord.Embed(color=0x7289da)
            embed.title = "Queued:"
            embed.description = (f'{song.name} `{converted_time}`')
            embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)


    @commands.check(is_wl)      
    @commands.command()
    async def pause(self, ctx):
        await check_in_vc(ctx)

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song = await player.pause()
        embed = discord.Embed(description=(f'Paused **{song.name}**.'), color=0x7289da)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl)      
    @commands.command()
    async def resume(self, ctx):
        await check_in_vc(ctx)

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song = await player.resume()
        embed = discord.Embed(description=(f'Resumed playing **{song.name}**.'), color=0x7289da)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl)       
    @commands.command()
    async def stop(self, ctx):
        await check_in_vc(ctx)

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        await player.stop()
        embed = discord.Embed(description=(f'Stopped playing audio.'), color=0x7289da)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl)        
    @commands.command()
    async def loop(self, ctx):
        await check_in_vc(ctx)

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song = await player.toggle_song_loop()
        if song.is_looping:
            embed = discord.Embed(description=(f'Enabled loop for **{song.name}**'), color=0x7289da)
            embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(description=(f'Disabled loop for **{song.name}**'), color=0x7289da)
            embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.check(is_wl)     
    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
            

        if len([song.name for song in player.current_queue()]) > 0:
            embed = discord.Embed(title=(f'Queue'), color=0x7289da)
            embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
            desc = ["**(showing the first 10 songs)**"]
            num = 0
            for song in player.current_queue():

                if num <= 10:
                    #print(num)
                    converted_time = await convertT(song.duration)
                    
                    desc.append(f'**{str(num)}.** '+ song.name + f' `{converted_time}`')
                    num += 1
            
            joined = "\n".join(desc)
            embed.description=(str(joined))
            

            await ctx.send(embed=embed)

    @commands.check(is_wl)      
    @commands.command(aliases=["nowplaying"])
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
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl)     
    @commands.command()                                                                                                                     #### TODO FIX ####
    async def skip(self, ctx):
        await check_in_vc(ctx)

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        data = await player.skip(force=True)
        
        embed = discord.Embed(description=(f'Skipped **{data[0].name}**'), color=0x7289da)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl) 
    @commands.command(aliases=["vol"])
    async def volume(self, ctx, vol:int ):
        await check_in_vc(ctx)

        if vol > 200:
            await ctx.channel.send('Volume cannot be greater than 200%!')
            return

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
        song, volume = await player.change_volume(float(vol / 100))
        embed = discord.Embed(description=(f"Changed volume for **{song.name}** to `{volume*100}%`"), color=0x7289da)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)

    @commands.check(is_wl)     
    @commands.command()
    async def remove(self, ctx, index):
        await check_in_vc(ctx)

        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            await not_pl(ctx)
            return
            
        try:
            song = await player.remove_from_queue(int(index))
        except IndexError:
            embed = discord.Embed(description=('The song you tried to remove does not exist!'), color=0xff0000)
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(description=(f'Removed **{song.name}** from the queue.'), color=0x7289da)
        embed.set_footer(text=f'Requested by: {ctx.author}', icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)





def setup(bot):
	bot.add_cog(Music(bot))