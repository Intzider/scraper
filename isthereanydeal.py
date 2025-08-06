import json
from random import sample, randint
import requests
from dotenv import load_dotenv

load_dotenv()

AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'AppleWebKit/537.36 (KHTML, like Gecko)',
    'Chrome/110.0.0.0',
    'Safari/537.36'
]


def create_new_header(cookie, itad):
    return {
        'user-agent': "".join([AGENTS[n] + " " for n in sample(range(len(AGENTS)), randint(1, len(AGENTS)))]).strip(),
        "content-type": "application/json",
        "cookie": f'visitor={cookie.get("visitor")}; sess2={cookie.get("sess2")}; country=HR',
        "Itad-SessionToken": itad,
    }


def get_hits():
    session = requests.Session()
    ses = session.get("https://isthereanydeal.com/giveaways/")
    itad = [json.loads('{' + x + '}').get('token', "") for x in ses.text.split(",") if "token" in x][0]

    url = "https://isthereanydeal.com/giveaways/api/list/?tab=live"
    data = { "offset": 0, "filter": None, "sort": None }

    x = requests.post(url, data=json.dumps(data), headers=create_new_header(ses.cookies.get_dict(), itad))

    hits = [x.get('url', "") for x in json.loads(x.text).get('data', [])]
    hits = [y for y in hits if 'indiegala' not in y]
    hits = ['<' + (y if "epicgames" not in y else y.split('&')[0]) + '>\n' for y in hits]
    return hits
