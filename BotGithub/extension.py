import discord
from discord.ext import commands

class extension(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    '''insert here the new commands!'''
    @commands.command
    async def example(self, ctx):
        await ctx.send("example")

def setup(bot):
    bot.add_cog(extension(bot))