import discord
import os
from urllib import request
from bs4 import BeautifulSoup
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
    print(message.author, ": ", message.content)

    # extract URLs
    extractor = URLExtract()
    URLs = list(extractor.gen_urls(message.content))

    # remove URLs from message
    text = message.content
    for i in range(len(URLs)):
        URL = URLs[i]
        if "https://" not in URL:
            URLs[i] = "https://" + URL

    # start storing attachments
    attachments = []

    # check for embeds
    if message.embeds:
        for embed in message.embeds:
            # store attachment
            attachment = {}
            attachment["URL"] = embed.url
            attachment["title"] = embed.title
            attachments.append(attachment)    
            # remove URL from URLs to prevent duplication
            URLs.remove(embed.url)

    # now get title for the remaining URLs
    for URL in URLs:
        # find title
        try:
            page = request.urlopen(URL, timeout=1)
            soup = BeautifulSoup(page, 'html.parser')
            title = soup.find('title').string
        except:
            title = ""

        # store attachment
        attachment = {}
        attachment["URL"] = URL
        attachment["title"] = title
        attachments.append(attachment)

    print("Attachments created!")
    print(*attachments, sep="\n")
  
    # get trello board
    all_boards = trello_client.list_boards()
    channel = message.channel.name
    print("Channel:", channel)
    Board = get_board(all_boards, "Dump")
    print(Board)
    # get/create list for channel
    List  = get_list(lists=Board.list_lists(), name=channel)
    if List is None:
        List = Board.add_list(channel)
    print(List)

    # create card for each attachment
    for attachment in attachments:
        if attachment["title"] != "":
            name = attachment["title"] + " - " + str(message.author.name)
        else:
            name = str(message.author.name)
        description = "This card was pulled automatically from Discord. Please categorize it properly."
        Card = List.add_card(name=name, desc=description)
        print(Card)

        Card.attach(
            name = attachment["title"],
            url  = attachment["URL"]
        )
        print("attached")


discord_client.run(os.getenv('DISCORD_TOKEN'))

