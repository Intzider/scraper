from enum import Enum


class Kvart(Enum):
    njuskalo = ["1248", "1257", "1258", "1260", "1261", "1262"]
    index = ["1248", "1257", "1258", "1260", "1261", "1262"]
    oglasnik = ["7445", "7582", "7600", "7662", "7669", "7679"]


class ClassName(Enum):
    njuskalo = "EntityList-item--Regular"
    index = "OglasiRezHolder"
    oglasnik = "oglasnik-box"


class Elem(Enum):
    njuskalo = "li"
    index = "div"
    oglasnik = "div"


class URIs(Enum):
    njuskalo = "https://www.njuskalo.hr"
    index = ""
    oglasnik = ""
