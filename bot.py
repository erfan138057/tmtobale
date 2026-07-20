import os
import json
import requests
from bs4 import BeautifulSoup


CHANNELS = [
    "akhbarefori",
    "appxa",
    "manchesterunited_passion",
    "FabrizioRomanoTG",
    "Squad_iran"
]

BALE_TOKEN = os.getenv("BALE_TOKEN")
BALE_CHAT_ID = os.getenv("BALE_CHAT_ID")

LAST_FILE = "last_ids.json"


def load_last_ids():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_last_ids(data):
    with open(LAST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_channel_posts(channel):
    url = f"https://t.me/s/{channel}"

    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        print(f"Failed: {channel}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    posts = soup.find_all(
        "div",
        class_="tgme_widget_message_text"
    )

    result = []

    for index, post in enumerate(posts):
        text = post.get_text("\n", strip=True)

        if text:
            result.append({
                "id": index,
                "text": text
            })

    return result


def send_to_bale(text):
    url = f"https://safir.bale.ai/v3/bot{BALE_TOKEN}/sendMessage"

    data = {
        "chat_id": BALE_CHAT_ID,
        "text": text
    }

    r = requests.post(url, json=data, timeout=20)

    if r.status_code == 200:
        print("Sent to Bale")
    else:
        print("Bale error:", r.text)


def main():

    last_ids = load_last_ids()

    for channel in CHANNELS:

        print("Checking:", channel)

        posts = get_channel_posts(channel)

        if not posts:
            continue

        last_seen = last_ids.get(channel, -1)

        new_posts = [
            p for p in posts
            if p["id"] > last_seen
        ]

        for post in new_posts:

            message = (
                f"📢 {channel}\n\n"
                f"{post['text']}"
            )

            send_to_bale(message)


        last_ids[channel] = posts[-1]["id"]


    save_last_ids(last_ids)


if __name__ == "__main__":
    main()
