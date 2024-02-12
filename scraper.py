import urllib.error
from copy import deepcopy
from time import sleep
from urllib.request import Request, urlopen
from random import sample, randint

from bs4 import BeautifulSoup as soup

from filters import *
from isthereanydeal import get_hits

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
        'User-Agent': "".join([AGENTS[n] + " " for n in sample(range(len(AGENTS)), randint(1, len(AGENTS)))]).strip()
    }


class Scraper:
    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    def __init__(self, to_scrape: dict, pages: int):

        self.__pages = pages
        self.__found = {"error": ""}

        try:
            for site, (urls, existing) in to_scrape.items():
                self.__parse_and_save(site, urls, existing)
        except KeyboardInterrupt:
            print("keyboard interrupt")
            pass

    def get_found(self) -> dict:
        if self.__found["error"] == "":
            self.__found.pop("error")
        return deepcopy(self.__found)

    def __parse_and_save(self, site: str, urls: list[str], existing: list[str]):
        new = []
        entries = []

        if site == 'isthereanydeal':
            entries = get_hits()
        else:
            for hit in self.__find_hits(site, urls):
                try:
                    entries = [URLs[site].value + str(path['href']) + "\n"
                               for path in hit.find_all('a')
                               if path.has_attr('href')]
                except TypeError:
                    pass
        for entry in entries:
            if entry in existing or entry in new:
                continue
            new.append(entry)

        if len(new) > 0:
            info = f"{site:<14} --> found new hits\n"
            self.__found[site] = "\n".join(new)
            print(info)
        else:
            info = f"{site:<14} --> no new hits\n"
            print(info, end="")

    def __find_hits(self, site: str, urls: list[str]) -> list:
        hits = []
        for index, url in enumerate(urls):
            retried = False
            for i in range(1, self.__pages + 1):
                print(urlopen(Request(f'{url}{"" if self.__pages == 1 else i}', headers=create_new_header())).read())
                try:
                    with urlopen(Request(f'{url}{"" if self.__pages == 1 else i}', headers=create_new_header())) as data:
                        new = soup(data.read(), "html.parser").findAll(Elem[site].value, {'class': [Class[site].value]})
                        print(new)
                        print(url, data.read(), soup(data.read(), "html.parser"))
                        if len(new) == 0:
                            info = f"{site:<10} --> ({index + 1}/{len(urls)}|{i}/{self.__pages}) captcha ?\n"
                            self.__found["error"] += info
                            print(info, end="")
                            if not retried:
                                retried = True
                                sleep(5)
                                i -= 1
                                continue
                            else:
                                break
                        hits += new
                except (urllib.error.URLError, urllib.error.HTTPError):
                    info = f"{site:<10} --> ({index + 1}/{len(urls)}|{i}/{self.__pages}) urllib exception\n"
                    self.__found["error"] += info
                    print(info, end="")
                    if not retried:
                        retried = True
                        sleep(5)
                        i -= 1

        return hits
