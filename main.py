import json
import os
from datetime import datetime

from mailer import send_email
from scraper import Scraper

__all__ = []


def load_config():
    with open(os.path.join(directory, 'config', "config.json"), "r") as file:
        return json.load(file)


def create_txt(file_name: str) -> list[str]:
    with open(os.path.join(directory, 'scraped', f'{email.split("@")[0]}_{file_name}.txt'), "a+") as file:
        file.seek(0)
        return file.readlines()


def update_txts():
    for file_name, data in items:
        if file_name != "info":
            with open(os.path.join(directory, 'scraped', f'{email.split("@")[0]}_{file_name}.txt'), "a+") as file:
                file.writelines(data)


def get_urls(kvartovi: str, site: str) -> list[str]:
    match site:
        case "njuskalo_najam":
            return [f"https://www.njuskalo.hr/iznajmljivanje-stanova"
                    f"?geo%5BlocationIds%5D={'%2C'.join(kvartovi)}"
                    f"&price%5Bmax%5D={config.get('price_najam_max', 500)}"
                    f"&page="]
        case "njuskalo":
            return [f"https://www.njuskalo.hr/prodaja-stanova"
                    f"?geo%5BlocationIds%5D={'%2C'.join(kvartovi)}"
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
                    for k in kvartovi]  # &vezani_na=988-887_562-563_978-1334
        case "oglasnik":
            return [f"https://www.oglasnik.hr/stanovi-prodaja"
                    f"?ad_params_44_from={config.get('m2_min', 44)}"
                    # f"&ad_price_from={config.get('price_min', 0)}"
                    f"&ad_price_to={config.get('price_max', 160000)}"
                    f"&ad_location_2%5B%5D=7442"
                    f"{''.join([f'&ad_location_3%5B{i}%5D={k}' for i, k in enumerate(kvartovi)])}"
                    f"&page="]
        case "isthereanydeal":
            return ["https://isthereanydeal.com/giveaways/"]
        case _:
            return []


if __name__ == "__main__":

    directory = os.path.dirname(os.path.abspath(__file__))
    time = datetime.now().strftime("%m/%d/%Y, %H:%M")
    configs = load_config()

    for email, config in configs.items():
        to_scrape = {name: (get_urls(config['visit'][name].get('kvart', []), name), create_txt(name))
                     for name, payload in config["visit"].items()
                     if payload.get('send', False)}
        items = Scraper(to_scrape, config.get('pages_max', 1)).get_found().items()
        additional_recipients = config.get('additional_recipients', [])
        all_recipients = [email] + additional_recipients
        for subject, body in items:
            send_email(directory, f"{subject} -- {time}", body, all_recipients)
        update_txts()
