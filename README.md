# go_rent_trello

## create env and install libs

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

to find\create credentials for trello [trello api creds](https://trello.com/app-key)

## to get trello board id

go to your dashboard, add *.json* to url and you need to find board id (or shortLink) -- TRELLO_BOARD_ID to .env
then you need to find needed column id (by name) in "lists" -- TRELLO_LIST_ID to .env

## .env file
```bash
TRELLO_API_KEY=ac2.....0ff80
TRELLO_API_TOKEN=85....bbcb01df
TRELLO_LIST_ID=6661...bdbf32d6
TRELLO_BOARD_ID=6661..f0f
```

