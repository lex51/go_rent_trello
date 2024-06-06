import requests
from load_dotenv import load_dotenv
import os
from datetime import datetime as dt
from loguru import logger as lg

load_dotenv()


lg.add("merge_trello_cards.log")


trello_board_id = os.environ.get("TRELLO_BOARD_ID")
trello_column_id = os.environ.get("TRELLO_LIST_ID")
cred_params = {
    "key": os.environ.get("TRELLO_API_KEY"),
    "token": os.environ.get("TRELLO_API_TOKEN"),
}

trello_card_labels = [
    "Партия",
]
trello_base_api = "https://api.trello.com/1"


def create_card(label_id: str = None):
    url = f"{trello_base_api}/cards"
    merged_card_data = {
        "name": f"Пошив-ИМЯ швеи - {dt.now().strftime('%d.%m.%y')}",
        "idList": trello_column_id,
        "idLabels": label_id,
    }
    resp_data = requests.post(
        url, params={**cred_params, **merged_card_data}
    ).json()  # or with params = cred_params | merged_card_data

    lg.info(f"created new card for merge\n{resp_data['shortUrl']}")
    return resp_data["id"]


def create_or_find_label():
    url = f"{trello_base_api}/labels"
    new_label_data = {"name": "Партия", "idBoard": trello_board_id, "color": "blue"}
    label_data = requests.post(url, params={**cred_params, **new_label_data}).json()
    return label_data["id"]


def add_checkitems_to_checklist(id_checklist: str, check_items: list):

    url = f"{trello_base_api}/checklists/{id_checklist}/checkItems"

    for item in check_items:
        checkitem_data = {"name": item, "id": id_checklist}
        requests.post(url, params={**cred_params, **checkitem_data})


def add_checklist_to_card(id_card: str, check_items: list):
    """
    check_items -- cards name"""
    url = f"{trello_base_api}/cards/{id_card}/checklists"
    add_checklist_data = {
        "name": "parrent cards",
        # "pos": "bottom"
        "pos": "top",
    }
    resp = requests.post(url, params={**cred_params, **add_checklist_data})
    if resp.status_code == 200:
        created_checklist_id = resp.json().get("id")
        # add items to created checklist
        add_checkitems_to_checklist(created_checklist_id, check_items)


def add_links_to_description(id_card: str, cards: list):

    url = f"{trello_base_api}/cards/{id_card}"
    # prepare links text
    desc_rows = [f'[{i["name"]}]({i["url"]} "")' for i in cards]
    add_description_data = {"desc": "\n".join(desc_rows)}
    requests.put(
        url,
        params={**cred_params, **add_description_data},
    )


def close_cards(cards: list):
    """
    move to archive"""
    moved_cards = []
    for card in cards:
        # pp(card)
        url = f"{trello_base_api}/cards/{card['id']}"
        add_description_data = {"closed": "true"}
        resp = requests.put(
            url,
            params={**cred_params, **add_description_data},
        )
        if resp.status_code == 200:
            moved_cards.append(card['shortUrl'])
        else:
            lg.warning("error on archived cards")
    lg.info(f"cards {', '.join(moved_cards)} are archived")


def get_all_column_cards():
    """
    find all cards in column without label"""
    resp = requests.get(
        url=f"{trello_base_api}/boards/{trello_board_id}/cards",
        params=cred_params,
    )
    if resp.status_code == 200:
        cards_data = resp.json()
        our_column_cards = []
        for card in cards_data:
            if card["idList"] == trello_column_id and not any(
                [
                    i
                    for i in card.get("labels", [])
                    if i.get("name") in trello_card_labels
                ]
            ):
                our_column_cards.append(card)
        lg.info(f"find {len(our_column_cards)} cards")
        return our_column_cards
    return None


@lg.catch
def start_merge_cards():

    # find all cards in
    cards_to_merge = get_all_column_cards()

    if cards_to_merge:
        # find or create label
        label_id = create_or_find_label()

        # create card with label
        created_card_id = create_card(label_id)

        # add checklist to card
        add_checklist_to_card(
            created_card_id, check_items=[i["name"] for i in cards_to_merge]
        )
        add_links_to_description(created_card_id, cards_to_merge)
        close_cards(cards_to_merge)


if __name__ == "__main__":
    start_merge_cards()
