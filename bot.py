import requests
from bs4 import BeautifulSoup

CHANNELS = [
    "akhbarefori",
    "appxa",
    "manchesterunited_passion",
    "FabrizioRomanoTG",
    "Squad_iran"
]


def get_messages(channel):
    url = f"https://t.me/s/{channel}"

    r = requests.get(url, timeout=20)

    if r.status_code != 200:
        print(f"Error {channel}: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    posts = soup.find_all("div", class_="tgme_widget_message_text")

    messages = []

    for post in posts:
        messages.append(post.get_text("\n", strip=True))

    return messages[-10:]


for channel in CHANNELS:
    print("\n================")
    print(channel)

    msgs = get_messages(channel)

    for m in msgs:
        print("----")
        print(m)
