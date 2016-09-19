from trello import TrelloClient
import settings
import argparse
import sys
import urllib2
import json
import re
from html2text import html2text
from jinja2 import Template

client = TrelloClient(settings.API_KEY, token=settings.TOKEN)

template_dir = "templates"

def read_template_file(name):
    return open(template_dir + "/" + name).read()

title_re = re.compile(read_template_file("title.regex"))
title_tmpl = Template(read_template_file("title.template"))
description_tmpl = Template(read_template_file("description.template"))

def find_board_with_name(name):
    boards = client.list_boards()
    for board in boards:
        if board.name == name:
            return board  
    return None

def board_command(args):    
    board = find_board_with_name(args.board_name)
    if board == None:
        print >> sys.stderr, 'Could not find board "%s"' % args.board_name
        return
    print 'Board name = "%s", Board id = "%s"' % (board.name, board.id)

def find_list_with_name(board, name):
    lsts = board.all_lists()
    for lst in lsts:
        if lst.name == name:
            return lst
    return None

def list_command(args):
    board = find_board_with_name(args.board_name)
    if board == None:
        print >> sys.stderr, 'Could not find board "%s"' % args.board_name
        return

    lst = find_list_with_name(board, args.list_name)
    if lst == None:
        if args.create:
            board.add_list(args.list_name)
            print 'Created list "%s"' % args.list_name
        else:
            print >> sys.stderr, 'Could not find list "%s"' % args.list_name
    else:
        print 'List name = "%s", List id = "%s"' % (lst.name, lst.id)



def fetch_proposals_from_funnel():
    talks = json.load(urllib2.urlopen(settings.FUNNEL_PAGE + "/json"))
    return talks['proposals']

def fetch_cards_from_board():
    board = client.get_board(settings.BOARD_ID)
    cards = board.all_cards()
    return cards

def group_cards_by_funnel_id(cards):
    cp = ((title_re.search(card.name), card) for card in cards)
    return dict((int(m.group("id")), card) for (m, card) in cp if m is not None)

def group_proposals_by_funnel_id(proposals):
    return dict((p["id"], p) for p in proposals)

def add_proposal_to_trello(lst, proposal):
    title = title_tmpl.render(**proposal)
    description = html2text(description_tmpl.render(**proposal))
    lst.add_card(name = title, desc = description)

def add_proposals_to_trello(proposals):
    lst = client.get_board(settings.BOARD_ID).get_list(settings.LIST_ID)
    for proposal in proposals:
        add_proposal_to_trello(lst, proposal)

def update_proposals_in_trello(proposals):
    pass

def sync_command(args):
    proposals = fetch_proposals_from_funnel()
    proposallookup = group_proposals_by_funnel_id(proposals)

    cards = fetch_cards_from_board()
    cardlookup = group_cards_by_funnel_id(cards)

    proposal_ids = set(proposallookup.keys())
    card_ids = set(cardlookup.keys())

    in_both = proposal_ids.intersection(card_ids)
    in_proposals_only = proposal_ids - card_ids


    proposals_to_add = (proposallookup[i] for i in in_proposals_only)
    add_proposals_to_trello(proposals_to_add)

    proposals_to_update = ((cardlookup[i], proposallookup[i]) for i in in_both)
    update_proposals_in_trello(proposals_to_update)

    
       
commands = {
    "board": board_command,
    "list": list_command,
    "sync": sync_command
}

def main():
    parser = argparse.ArgumentParser(prog="funnel-trello-client")
    subparsers = parser.add_subparsers(help="subcommands")

    board_parser = subparsers.add_parser('board', help='Get details about a board')
    board_parser.add_argument('board_name',type=str, help="The name of the board")

    list_parser = subparsers.add_parser('list', help='Get details about a list')
    list_parser.add_argument('board_name', type=str, help="The name of the board")
    list_parser.add_argument('list_name', type=str, help="The name of the list")
    list_parser.add_argument('-c', '--create', help="Create this list if it doesn't exist", action="store_true")

    sync_parser = subparsers.add_parser('sync', help='Sync the funnel talks with trello')


    args = parser.parse_args()
    command = commands[sys.argv[1]]
    command(args)


if __name__ == "__main__":
    main()