import discord
from discord.ext import commands
import yt_dlp

# Configuração do bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Lista de músicas
queue = []

# Configuração do yt_dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

def search_youtube(query):
    with yt_dlp.YoutubeDL({"format": "bestaudio", "quiet": True}) as ydl:
        try:
            results = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"]
            return results[0]["url"] if results else None
        except Exception as e:
            print(f"Erro ao buscar música: {e}")
            return None

def play_next(ctx):
    if queue:
        url = queue.pop(0)
        play_song(ctx, url)

def play_song(ctx, url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['url']
        ctx.voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: play_next(ctx))

@bot.event
async def on_ready():
    print(f'Logado como {bot.user}')

async def join_and_welcome(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        
        # Tocar som padrão ao entrar
        url = search_youtube("Welcome Sound")  # Substitua por um som específico
        if url:
            play_song(ctx, url)
            while ctx.voice_client.is_playing():  # Aguarda o som terminar antes de continuar
                await discord.utils.sleep(1)
    else:
        await ctx.send("Você precisa estar em um canal de voz!")

@bot.command()
async def join(ctx):
    await join_and_welcome(ctx)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Não estou em um canal de voz.")

@bot.command()
async def play(ctx, *, query: str):
    if not ctx.voice_client:
        await join_and_welcome(ctx)
    
    url = search_youtube(query)
    if not url:
        await ctx.send("Não consegui encontrar a música.")
        return
    
    if ctx.voice_client.is_playing():
        queue.append(url)
        await ctx.send("Música adicionada à fila!")
    else:
        play_song(ctx, url)

@bot.command()
async def skip(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        play_next(ctx)

bot.run("SEU_TOKEN_AQUI")
