from urllib import request
from bs4 import BeautifulSoup

def get_board(boards, name):
    for board in boards:
        if board.name == name:
            return board
    return None

def get_list(lists, name):
    for item in lists:
        if item.name == name:
            return item
    return None

def get_attachments(message, URLs):
    # add https:// to URLs 
    for i in range(len(URLs)):
        URL = URLs[i]
        if "https://" not in URL and "http://" not in URL:
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
        # find title, otherwise just use the URL
        try:
            page = request.urlopen(URL, timeout=2)
            soup = BeautifulSoup(page, 'html.parser')
            title = soup.find('title').string
        except:
            title = URL

        # store attachment
        attachment = {}
        attachment["URL"] = URL
        attachment["title"] = title
        attachments.append(attachment)

    return attachments

def create_card(List, author, attachment):
    name = attachment["title"] + " - " + author
    description = "This card was pulled automatically from Discord. Please categorize it properly."
    Card = List.add_card(name=name, desc=description)
    print(Card)

    result = Card.attach(
            name = attachment["title"],
            url  = attachment["URL"]
        )

    return result['id']