import os
import urllib.error
from copy import deepcopy
from urllib.request import Request, urlopen
from random import sample, randint
from datetime import datetime
from time import sleep

from bs4 import BeautifulSoup as soup

from filters import *

__all__ = ["Scraper"]

AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'AppleWebKit/537.36 (KHTML, like Gecko)',
    'Chrome/110.0.0.0',
    'Safari/537.36'
]


def create_new_header():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': "".join([AGENTS[n] + " " for n in sample(range(len(AGENTS)), randint(1, len(AGENTS)))]).strip(),
    }


class Scraper:
    def __init__(self, main_directory: str, to_scrape: dict, pages: int):
        self.__main_directory = main_directory
        self.__pages = pages
        self.__found = {}

        for site, urls in to_scrape.items():
            self.__parse_and_save(site, urls)

    def get_found(self):
        return deepcopy(self.__found)

    def __parse_and_save(self, site: str, urls: list[str]):
        with open(os.path.join(self.__main_directory, site + ".txt"), "r+") as f:
            time = datetime.now().strftime("%m/%d/%Y, %H:%M")
            new = []
            existing = f.readlines()

            for flat in self.__find_flats(site, urls):
                try:
                    entries = [URLs[site].value + str(path['href']) + "\n" for path in flat.find_all('a')]
                    for entry in entries:
                        if entry in existing or entry in new:
                            continue
                        new.append(entry)
                except TypeError:
                    pass

            if len(new) > 0:
                f.writelines(new)
                self.__found[f"{site} -- {time}"] = "\n".join(new)

    def __find_flats(self, site: str, urls: list[str]):
        flats = []

        for url in urls:
            print(site, end="")
            for i in range(1, self.__pages + 1):
                print(i, end="" if i != self.__pages else "\n")
                try:
                    with urlopen(Request(f'{url}{i}', headers=create_new_header())) as data:
                        new = soup(data.read(), "html.parser").findAll(Elem[site].value, {'class': [Class[site].value]})
                        if len(new) == 0:
                            print("captcha")
                            break
                        flats += new
                    sleep(30)
                except urllib.error:
                    pass

        return flats
