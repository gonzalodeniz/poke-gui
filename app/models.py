from dataclasses import dataclass
from typing import List


def _title_case(text: str) -> str:
    return text.replace('-', ' ').title()


@dataclass
class PokemonStat:
    name: str
    value: int

    @classmethod
    def from_api(cls, data: dict) -> "PokemonStat":
        stat_name = _title_case(data.get("stat", {}).get("name", ""))
        return cls(name=stat_name, value=data.get("base_stat", 0))

    def to_dict(self) -> dict:
        return {"name": self.name, "value": self.value}


@dataclass
class Pokemon:
    identifier: int
    name: str
    description: str
    height_m: float
    weight_kg: float
    types: List[str]
    abilities: List[str]
    stats: List[PokemonStat]
    image_url: str

    @classmethod
    def from_api(cls, data: dict, description: str) -> "Pokemon":
        types = [_title_case(entry["type"]["name"]) for entry in data.get("types", [])]
        abilities = [_title_case(entry["ability"]["name"]) for entry in data.get("abilities", [])]
        stats = [PokemonStat.from_api(entry) for entry in data.get("stats", [])]
        sprites = data.get("sprites", {})
        official_artwork = sprites.get("other", {}).get("official-artwork", {}).get("front_default")
        default_sprite = sprites.get("front_default")
        image_url = official_artwork or default_sprite or ""
        height_m = round((data.get("height", 0) or 0) / 10, 2)
        weight_kg = round((data.get("weight", 0) or 0) / 10, 2)

        return cls(
            identifier=data.get("id", 0),
            name=_title_case(data.get("name", "")),
            description=description,
            height_m=height_m,
            weight_kg=weight_kg,
            types=types,
            abilities=abilities,
            stats=stats,
            image_url=image_url,
        )

    def to_dict(self) -> dict:
        return {
            "id": self.identifier,
            "name": self.name,
            "description": self.description,
            "height_m": self.height_m,
            "weight_kg": self.weight_kg,
            "types": self.types,
            "abilities": self.abilities,
            "stats": [stat.to_dict() for stat in self.stats],
            "image_url": self.image_url,
            "total_stats": self.total_stats,
        }

    @property
    def total_stats(self) -> int:
        return sum(stat.value for stat in self.stats)


@dataclass
class PokemonSummary:
    identifier: int
    name: str

    @classmethod
    def from_url(cls, name: str, url: str) -> "PokemonSummary":
        identifier = 0
        if url:
            try:
                identifier = int(url.rstrip("/").split("/")[-1])
            except (ValueError, AttributeError):
                identifier = 0
        return cls(identifier=identifier, name=_title_case(name))

    def to_dict(self) -> dict:
        return {"id": self.identifier, "name": self.name}
