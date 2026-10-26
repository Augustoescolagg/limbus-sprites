
import os
import re
import time
import zipfile
import requests
from urllib.parse import quote

API = "https://limbuscompany.wiki.gg/api.php"

GROUPS = {
    "The_Thumb": ["Valencina", "Lucio"],
    "The_Index": ["Rien", "Sora"],
    "The_Middle": ["Matthias", "Kira"],
    "The_Ring": ["Callisto", "Albina"],
    "The_Pinky": ["Shiomi Yoru", "Ren"],
}

session = requests.Session()
session.headers["User-Agent"] = "LimbusSpriteCollector/1.0"

def search_files(name):
    found = {}
    queries = [name, name.replace(" ", "_")]

    for term in queries:
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srnamespace": 6,
            "srsearch": term,
            "srlimit": 100,
        }

        try:
            data = session.get(API, params=params, timeout=30).json()
            for page in data.get("query", {}).get("search", []):
                title = page["title"]
                if name.lower().replace("_", " ") in title.lower().replace("_", " "):
                    found[title] = True
        except Exception as e:
            print("Erro na busca:", e)

    return list(found)

def image_url(title):
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url",
    }
    data = session.get(API, params=params, timeout=30).json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        info = page.get("imageinfo", [])
        if info:
            return info[0]["url"]
    return None

def safe(text):
    return re.sub(r'[<>:"/\\|?*]', "_", text)

os.makedirs("sprites", exist_ok=True)
count = 0

with zipfile.ZipFile("Limbus_Sprites.zip", "w",
                     zipfile.ZIP_DEFLATED) as z:
    for faction, characters in GROUPS.items():
        for character in characters:
            print("Buscando", character)
            for title in search_files(character):
                try:
                    url = image_url(title)
                    if not url:
                        continue
                    response = session.get(url, timeout=60)
                    response.raise_for_status()
                    if not response.headers.get("Content-Type", "").startswith("image/"):
                        continue

                    filename = safe(title.replace("File:", ""))
                    path = f"{faction}/{safe(character)}/{filename}"
                    z.writestr(path, response.content)
                    count += 1
                    print("  Baixado:", filename)
                    time.sleep(0.2)
                except Exception as e:
                    print("  Falhou:", title, e)

print("Total de imagens:", count)
print("ZIP criado: Limbus_Sprites.zip")
