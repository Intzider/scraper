import json
import os
from random import sample, randint
from datetime import datetime
from urllib.request import Request, urlopen
from time import sleep

from filters import *
from bs4 import BeautifulSoup as soup
from mailer import send_email

DIR = os.path.dirname(os.path.abspath(__file__))

AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'AppleWebKit/537.36 (KHTML, like Gecko)',
    'Chrome/110.0.0.0',
    'Safari/537.36'
]


def load_config():
    with open(os.path.join(DIR, "config.json"), "r") as file:
        return json.load(file)


def create_txt(file_name: str):
    open(os.path.join(DIR, file_name), "a+").close()


def create_new_header():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': "".join([AGENTS[n] + " " for n in sample(range(len(AGENTS)), randint(1, len(AGENTS)))]).strip(),
    }


def get_index_urls():
    return [f"https://www.index.hr/oglasi/prodaja-stanova/gid/3278?pojamZup=1153&tipoglasa=1&sortby=1&elementsNum=10"
            f"&grad={k.value}&naselje=0"
            f"&attr_Int_988={config.get('m2_min', 44)}"
            f"&attr_Int_887={config.get('m2_max', '')}"
            f"&cijenaod={config.get('price_min', 0)}"
            f"&cijenado={config.get('price_max', 160000)}"
            f"&num="
            for k in Kvart]  # &vezani_na=988-887_562-563_978-1334


def get_njuskalo_urls():
    return [f"https://www.njuskalo.hr/prodaja-stanova"
            f"?geo%5BlocationIds%5D={'%2C'.join([k.value for k in Kvart])}"
            f"&price%5Bmin%5D={config.get('price_min', 0)}"
            f"&price%5Bmax%5D={config.get('price_max', 160000)}"
            f"&flatBuildingType=flat-in-residential-building"
            f"&livingArea%5Bmin%5D={config.get('m2_min', 44)}"
            f"&page="]


def get_urls(site: str):
    if site == "njuskalo":
        return get_njuskalo_urls()
    elif site == "index":
        return get_index_urls()


def get_flats(site: str, urls: list[str]):
    condos = []

    for url in urls:
        print(site, end="")
        for i in range(1, config.get("max_pages", 1) + 1):
            print(i, end="" if i != config.get("max_pages", 1) else "\n")
            with urlopen(Request(url + str(i), headers=create_new_header())) as data:
                new = soup(data.read(), "html.parser").findAll(Elem[site].value, {'class': [ClassName[site].value]})
                if len(new) == 0:
                    print("captcha")
                    condos += ["captcha\n"]
                    break
                condos += new
            sleep(30)
        condos += ["-----------------------------------------------"]
    return condos


def find_and_send(site: str):
    create_txt(site + "_visited.txt")
    with open(os.path.join(DIR, site + "_visited.txt"), "r+") as f:
        time = datetime.now().strftime("%m/%d/%Y, %H:%M")
        new = []
        existing = f.readlines()

        for flat in get_flats(site, get_urls(site)):
            try:
                entry = URIs[site].value + str(flat.find('a')['href']) + "\n"
                if entry in existing:
                    continue
                new.append(entry)
            except TypeError:
                pass

        if len(new) > 0:
            f.writelines(new)
            send_email(site, time, "\n".join(new), config["recipients"])


if __name__ == "__main__":
    config = load_config()

    for name, visit in config["visit"].items():
        if visit:
            find_and_send(name)
