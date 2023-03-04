from enum import Enum


class Kvart(Enum):
    njuskalo_najam = ["1248", "1257", "1258", "1260", "1261", "1262"]
    njuskalo = ["1248", "1257", "1258", "1260", "1261", "1262"]
    index = ["1248", "1257", "1258", "1260", "1261", "1262"]
    oglasnik = ["7445", "7582", "7600", "7662", "7669", "7679"]


class Class(Enum):
    njuskalo_najam = "EntityList-item--Regular"
    njuskalo = "EntityList-item--Regular"
    index = "OglasiRezHolder"
    oglasnik = "oglasnik-box"


class Elem(Enum):
    njuskalo_najam = "li"
    njuskalo = "li"
    index = "div"
    oglasnik = "div"


class URLs(Enum):
    njuskalo_najam = "https://www.njuskalo.hr"
    njuskalo = "https://www.njuskalo.hr"
    index = ""
    oglasnik = ""
