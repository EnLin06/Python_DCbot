import discord
from discord.ext import commands

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = "/", intents = intents)

@bot.event
async def on_ready():
    print(f"目前登入身份 --> {bot.user}")

@bot.command()
async def sayHI(ctx):
    await ctx.send("HI !")

bot.run("DCBot TOKEN")
