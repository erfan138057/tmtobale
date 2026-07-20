import requests
from bs4 import BeautifulSoup

channel = "FabrizioRomanoTG"

url = f"https://t.me/s/{channel}"

response = requests.get(url)

print(response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

messages = soup.find_all("div", class_="tgme_widget_message_text")

for msg in messages[-10:]:
    print("------")
    print(msg.get_text("\n"))
