import json
import os
from random import sample, randint
from datetime import datetime
from urllib.request import Request, urlopen
from time import sleep

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


def create_txt(name: str):
    open(os.path.join(DIR, name + ".txt"), "a+").close()


def create_new_header():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': "".join([AGENTS[n] + " " for n in sample(range(len(AGENTS)), randint(1, len(AGENTS)))]).strip(),
    }


def get_site_url():
    uri = "https://www.njuskalo.hr"
    w = "/prodaja-stanova"
    q = {
        "location": "?geo%5BlocationIds%5D=1248%2C1262%2C1260%2C1261%2C1258%2C1257",
        "price_max": "&price%5Bmax%5D=" + str(config.get("price_max", 150000)),
        "building_type": "&flatBuildingType=flat-in-residential-building",
        "m2_min": "&livingArea%5Bmin%5D=" + str(config.get("m2_min", 45)),
        "page": "&page=",
    }

    return uri + w + q["location"] + q["price_max"] + q["building_type"] + q["m2_min"] + q["page"]


def get_flats():
    condos = []

    for i in range(1, config.get("max_pages", 1) + 1):
        print(i, end="" if i != config.get("max_pages", 1) else "\n")
        with urlopen(Request(get_site_url() + str(i), headers=create_new_header())) as site_data:
            new_stuff = soup(site_data.read(), "html.parser").findAll('li', {'class': ['EntityList-item--Regular']})
            if len(new_stuff) == 0:
                print("captcha", end="")
                break
            condos += new_stuff
        sleep(30)
    return condos


if __name__ == "__main__":
    create_txt("njuskalo_visited")
    config = load_config()

    with open(os.path.join(DIR, "njuskalo_visited.txt"), "r+") as f:
        new = [datetime.now().strftime("%m/%d/%Y, %H:%M") + "\n"]
        existing = f.readlines()

        for flat in get_flats():
            try:
                entry = "https://www.njuskalo.hr" + str(flat.find('h3').find('a')['href']) + "\n"
                if entry in existing:
                    continue
                new.append(entry)
            except TypeError:
                print("site change?")

        if len(new) > 1:
            f.writelines(new)
            send_email("njuskalo", "\n".join(new), config["recipients"])
