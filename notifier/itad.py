import json

import requests

BASE = "https://isthereanydeal.com/giveaways/"
LIST_API = BASE + "api/list/?tab=live"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
EXCLUDED = ("indiegala",)


def _session_token(html: str) -> str:
    """The giveaways page embeds a session token the list API requires."""
    for chunk in html.split(","):
        if '"token"' in chunk:
            return json.loads("{" + chunk + "}").get("token", "")
    raise RuntimeError("ITAD session token not found, page layout probably changed")


def _clean(url: str) -> str:
    # epic links carry tracking params that change between requests
    return url.split("&")[0] if "epicgames" in url else url


def fetch_giveaways() -> list[str]:
    session = requests.Session()
    session.headers["user-agent"] = USER_AGENT

    page = session.get(BASE, timeout=30)
    page.raise_for_status()

    response = session.post(
        LIST_API,
        json={"offset": 0, "filter": None, "sort": None},
        headers={"Itad-SessionToken": _session_token(page.text)},
        cookies={"country": "HR"},
        timeout=30,
    )
    response.raise_for_status()

    urls = [item.get("url", "") for item in response.json().get("data", [])]
    return [_clean(u) for u in urls if u and not any(x in u for x in EXCLUDED)]
