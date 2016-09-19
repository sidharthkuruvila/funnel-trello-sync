This is a simple command line script to push funnel proposals into a Trello board.

Setting up
==========

Create settings.py

    cp settings-example.py settings.py

The the values for API_KEY and TOKEN from trello. Set FUNNEL_PAGE to the page of the talk you want to sync.

To get the id of a board given it's name run

    python funnel-trello-sync.py board "Board Name"

To get the create a list in the board

    python funnel-trello-sync.py list -c "Board Name" "List Name"

Copy the board and list ids printed out from the earlier commands and paste them into settings.py.


Running Sync
============

    python funnel-trello-sync.py sync