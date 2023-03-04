import json
import os

from filters import Kvart
from mailer import send_email
from scraper import Scraper

DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(os.path.join(DIR, "config.json"), "r") as file:
        return json.load(file)


def create_txt(file_name: str):
    open(os.path.join(DIR, file_name + ".txt"), "a+").close()


def get_urls(site: str):
    match site:
        case "njuskalo":
            return [f"https://www.njuskalo.hr/prodaja-stanova"
                    f"?geo%5BlocationIds%5D={'%2C'.join(Kvart[site].value)}"
                    f"&price%5Bmin%5D={config.get('price_min', 0)}"
                    f"&price%5Bmax%5D={config.get('price_max', 160000)}"
                    f"&flatBuildingType=flat-in-residential-building"
                    f"&livingArea%5Bmin%5D={config.get('m2_min', 44)}"
                    f"&page="]
        case "index":
            return [f"https://www.index.hr/oglasi/prodaja-stanova/gid/3278"
                    f"?pojamZup=1153&tipoglasa=1&sortby=1&elementsNum=10"
                    f"&grad={k}&naselje=0"
                    f"&attr_Int_988={config.get('m2_min', 44)}"
                    f"&attr_Int_887={config.get('m2_max', '')}"
                    f"&cijenaod={config.get('price_min', 0)}"
                    f"&cijenado={config.get('price_max', 160000)}"
                    f"&num="
                    for k in Kvart[site].value]  # &vezani_na=988-887_562-563_978-1334
        case "oglasnik":
            return [f"https://www.oglasnik.hr/stanovi-prodaja"
                    f"?ad_params_44_from={config.get('m2_min', 44)}"
                    # f"&ad_price_from={config.get('price_min', 0)}"
                    f"&ad_price_to={config.get('price_max', 160000)}"
                    f"&ad_location_2%5B%5D=7442"
                    f"{''.join([f'&ad_location_3%5B{i}%5D={k}' for i, k in enumerate(Kvart[site].value)])}"
                    f"&page="]
        case _:
            return []


if __name__ == "__main__":
    config = load_config()
    to_scrape = {name: get_urls(name) for name, visit in config["visit"].items() if visit}

    scraper = Scraper(DIR, to_scrape, config.get('pages_max', 1))
    for subject, body in scraper.get_found().items():
        send_email(subject, body, config.get('recipients'))