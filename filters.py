from enum import Enum


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
