import json
import os
import urllib.error
from random import sample, randint
from datetime import datetime
from urllib.request import Request, urlopen
from time import sleep

from bs4 import BeautifulSoup as soup

from filters import *
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
    open(os.path.join(DIR, file_name + ".txt"), "a+").close()


def create_new_header():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': "".join([AGENTS[n] + " " for n in sample(range(len(AGENTS)), randint(1, len(AGENTS)))]).strip(),
    }


def get_urls(site: str):
    if site == "njuskalo":
        return [f"https://www.njuskalo.hr/prodaja-stanova"
                f"?geo%5BlocationIds%5D={'%2C'.join(Kvart[site].value)}"
                f"&price%5Bmin%5D={config.get('price_min', 0)}"
                f"&price%5Bmax%5D={config.get('price_max', 160000)}"
                f"&flatBuildingType=flat-in-residential-building"
                f"&livingArea%5Bmin%5D={config.get('m2_min', 44)}"
                f"&page="]
    elif site == "index":
        return [f"https://www.index.hr/oglasi/prodaja-stanova/gid/3278"
                f"?pojamZup=1153&tipoglasa=1&sortby=1&elementsNum=10"
                f"&grad={k}&naselje=0"
                f"&attr_Int_988={config.get('m2_min', 44)}"
                f"&attr_Int_887={config.get('m2_max', '')}"
                f"&cijenaod={config.get('price_min', 0)}"
                f"&cijenado={config.get('price_max', 160000)}"
                f"&num="
                for k in Kvart[site].value]  # &vezani_na=988-887_562-563_978-1334
    elif site == "oglasnik":
        return [f"https://www.oglasnik.hr/stanovi-prodaja"
                f"?ad_params_44_from={config.get('m2_min', 44)}"
                # f"&ad_price_from={config.get('price_min', 0)}"
                f"&ad_price_to={config.get('price_max', 160000)}"
                f"&ad_location_2%5B%5D=7442"
                f"{''.join([f'&ad_location_3%5B{i}%5D={k}' for i, k in enumerate(Kvart[site].value)])}"
                f"&page="]


def get_flats(site: str, urls: list[str]):
    condos = []

    for url in urls:
        print(site, end="")
        for i in range(1, config.get("max_pages", 1) + 1):
            print(i, end="" if i != config.get("max_pages", 1) else "\n")
            try:
                with urlopen(Request(url + str(i), headers=create_new_header())) as data:
                    new = soup(data.read(), "html.parser").findAll(Elem[site].value, {'class': [ClassName[site].value]})
                    if len(new) == 0:
                        print("captcha")
                        condos += ["captcha\n"]
                        break
                    condos += new
                sleep(30)
            except urllib.error:
                pass

    return condos


def find_and_send(site: str):
    create_txt(site)
    with open(os.path.join(DIR, site + ".txt"), "r+") as f:
        time = datetime.now().strftime("%m/%d/%Y, %H:%M")
        new = []
        existing = f.readlines()

        for flat in get_flats(site, get_urls(site)):
            try:
                entries = [URIs[site].value + str(fl['href']) + "\n" for fl in flat.find_all('a')]
                for entry in entries:
                    if entry in existing or entry in new:
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
