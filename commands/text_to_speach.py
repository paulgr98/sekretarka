import discord
from gtts import gTTS
import asyncio


class TextToSpeach:
    def __init__(self, client):
        self._client: discord.Client = client
        self._filename = 'tts.mp3'

    async def is_already_in_voice_channel(self, ctx) -> bool:
        voice = discord.utils.get(self._client.voice_clients, guild=ctx.guild)
        if voice:
            return True
        return False

    async def join_voice_channel(self, ctx) -> discord.VoiceClient | None:
        if not ctx.author.voice:
            await ctx.send('Najpierw dołącz do kanału głosowego')
            return
        if await self.is_already_in_voice_channel(ctx):
            return discord.utils.get(self._client.voice_clients, guild=ctx.guild)
        voice_channel = ctx.author.voice.channel
        voice = discord.utils.get(self._client.voice_clients, guild=ctx.guild)
        if not voice:
            await voice_channel.connect()
            voice = discord.utils.get(self._client.voice_clients, guild=ctx.guild)
        return voice

    async def leave_voice_channel(self, ctx) -> None:
        voice = discord.utils.get(self._client.voice_clients, guild=ctx.guild)
        if voice:
            await voice.disconnect(force=True)

    async def text_to_speach(self, ctx, text) -> None:
        voice = discord.utils.get(self._client.voice_clients, guild=ctx.guild)
        joined_vc = False
        if not voice:
            voice = await self.join_voice_channel(ctx)
            joined_vc = True
        if not voice:
            return
        tts = gTTS(text=text, lang='pl', slow=False)
        tts.save(self._filename)

        def after_playing(error):
            if joined_vc:
                coro = self.leave_voice_channel(ctx)
                fut = asyncio.run_coroutine_threadsafe(coro, self._client.loop)
                fut.result()

        voice.play(discord.FFmpegPCMAudio(self._filename), after=after_playing)
