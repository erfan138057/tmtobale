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

    try:
        response = requests.get(
            url,
            timeout=20,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

    except Exception as e:
        print("Request error:", e)
        return []


    if response.status_code != 200:
        print(channel, "failed:", response.status_code)
        return []


    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )


    messages = soup.find_all(
        "div",
        class_="tgme_widget_message"
    )


    result = []


    for msg in messages:

        post_id = msg.get("data-post")

        text_box = msg.find(
            "div",
            class_="tgme_widget_message_text"
        )


        if not post_id:
            continue


        text = ""

        if text_box:
            text = text_box.get_text(
                "\n",
                strip=True
            )


        if text:
            result.append(
                {
                    "id": post_id,
                    "text": text
                }
            )


    return result



def send_to_bale(text):

    if not BALE_TOKEN or not BALE_CHAT_ID:
        print("❌ Bale secrets missing")
        return

    url = (
        f"https://tapi.bale.ai/bot"
        f"{BALE_TOKEN}/sendMessage"
    )

    payload = {
        "chat_id": BALE_CHAT_ID,
        "text": text
    }

    try:
        r = requests.post(
            url,
            json=payload,
            timeout=20
        )

        if r.status_code == 200:
            result = r.json()

            if result.get("ok"):
                print("✅ Sent to Bale")
            else:
                print("❌ Bale API Error:", result)

        else:
            print("❌ HTTP Error:", r.status_code)
            print(r.text)

    except Exception as e:
        print("❌ Connection Error:", e)




def main():

    last_ids = load_last_ids()


    for channel in CHANNELS:

        print("\nChecking:", channel)


        posts = get_channel_posts(channel)


        if not posts:
            continue



        last_seen = last_ids.get(
            channel,
            ""
        )


        new_posts = []


        for post in posts:

            if post["id"] > last_seen:
                new_posts.append(post)



        for post in new_posts:

            message = (
                f"📢 {channel}\n\n"
                f"{post['text']}"
            )

            send_to_bale(message)



        if posts:

            last_ids[channel] = posts[-1]["id"]



    save_last_ids(last_ids)



if __name__ == "__main__":
    main()
