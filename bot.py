import discord
import os
from helpers import *
from discord.ext import commands
from trello import TrelloClient
from urlextract import URLExtract

discord_client = commands.Bot(command_prefix=".")
trello_client = TrelloClient(
    api_key    = os.getenv('TRELLO_API_KEY'),
    api_secret = os.getenv('TRELLO_API_SECRET'),
    # token='your-secret',
    # token_secret='your-oauth-token-secret'
)

@discord_client.event
async def on_ready():
    print('Bot is ready.')


@discord_client.event
async def on_message(message):
    # print message
    # print(message.author, ": ", message.content)

    if message.author.bot:
        return

    # extract URLs
    extractor = URLExtract()
    URLs = list(extractor.gen_urls(message.content))

    # ignore message if there were no URLs
    if URLs == []:
        return
    
    # create attachments from URLs
    attachments = get_attachments(message, URLs)
    
    # print("Attachments created!")
    # print(*attachments, sep="\n")
  
    # get trello board
    all_boards = trello_client.list_boards()
    channel = message.channel.name
    Board = get_board(all_boards, "Dump")

    # get/create list for channel
    List  = get_list(lists=Board.list_lists(), name=channel)
    if List is None:
        List = Board.add_list(channel)

    # create card for each attachment
    attached = []
    for attachment in attachments:
        author = str(message.author.name)
        result = create_card(List, author, attachment)
        attached.append(result)

    if len(attached) == len(attachments):
        await message.channel.send('I have attached these links to Trello for you. Please remember to organise them at https://trello.com/b/SAJvonRo/dump.')
    else:
        await message.channel.send('Oops! Something went wrong. Please attach these links manually to https://trello.com/.')


discord_client.run(os.getenv('DISCORD_TOKEN'))

