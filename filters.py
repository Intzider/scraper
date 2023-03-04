from enum import Enum


class Kvart(Enum):
    crnomerec = "1248"
    podsljeme = "1257"
    podsusedvrapce = "1258"
    stenjevec = "1260"
    tresnjevkajug = "1261"
    tresnjevkasjever = "1262"


class ClassName(Enum):
    njuskalo = "EntityList-item--Regular"
    index = "OglasiRezHolder"


class Elem(Enum):
    njuskalo = "li"
    index = "div"


class URIs(Enum):
    njuskalo = "https://www.njuskalo.hr"
    index = ""
