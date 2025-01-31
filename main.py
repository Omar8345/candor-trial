import discord
from discord.ext import commands
import json

with open('config.json', 'r') as f:
    config = json.load(f)

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

TICKET_SUPPORT_ROLE_ID = config['TICKET_SUPPORT_ROLE_ID']
TOKEN = config['TOKEN']

user_tickets = []
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def ticket(ctx):
    if any(ticket['userID'] == ctx.author.id for ticket in user_tickets):
        await ctx.reply('You already have a ticket.')
        return
    
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        ctx.guild.get_role(TICKET_SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }

    channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.name}', overwrites=overwrites)

    await channel.send(f'{ctx.author.mention} Please wait for support to assist you.')

    user_tickets.append({
        'userID': ctx.author.id,
        'channelID': channel.id
    })

    await ctx.reply(f'Ticket created: {channel.mention}')

@bot.command()
async def close(ctx):
    user_roles = [role.id for role in ctx.author.roles]
    if TICKET_SUPPORT_ROLE_ID not in user_roles:
        await ctx.reply('You do not have permission to close tickets.')
        return
    
    ticket = next((ticket for ticket in user_tickets if ticket['channelID'] == ctx.channel.id), None)
    if ticket is None:
        await ctx.reply('This is not a ticket channel.')
        return
    
    await ctx.channel.delete()
    user_tickets.remove(ticket)


bot.run(TOKEN)