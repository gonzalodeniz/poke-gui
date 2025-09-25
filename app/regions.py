from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Dict, List


@dataclass(frozen=True)
class RegionInfo:
    key: str
    name: str
    pokedex: str
    description: str
    map_image: str
    featured: List[int]


class PokemonRegions:
    """Static catalogue describing Pokémon regions and helper accessors."""

    _REGIONS: ClassVar[Dict[str, RegionInfo]] = {
        "kanto": RegionInfo(
            key="kanto",
            name="Kanto",
            pokedex="kanto",
            description="La región clásica donde empezó la aventura de Ash y Pikachu.",
            map_image="https://i.imgur.com/eJ6aZ0x.png",
            featured=[25, 1, 4],
        ),
        "johto": RegionInfo(
            key="johto",
            name="Johto",
            pokedex="original-johto",
            description="Cascadas y bosques donde los Pokémon guardan tradiciones ancestrales.",
            map_image="https://i.imgur.com/dY1W13f.png",
            featured=[152, 155, 158],
        ),
        "hoenn": RegionInfo(
            key="hoenn",
            name="Hoenn",
            pokedex="hoenn",
            description="Un archipiélago tropical rebosante de aventuras acuáticas.",
            map_image="https://i.imgur.com/Dpfr9GS.png",
            featured=[252, 255, 258],
        ),
        "sinnoh": RegionInfo(
            key="sinnoh",
            name="Sinnoh",
            pokedex="original-sinnoh",
            description="Montañas nevadas y leyendas antiguas se cruzan en cada ruta.",
            map_image="https://i.imgur.com/8f5nHgo.png",
            featured=[387, 390, 393],
        ),
        "unova": RegionInfo(
            key="unova",
            name="Unova",
            pokedex="original-unova",
            description="Una metrópoli vibrante inspirada en grandes ciudades modernas.",
            map_image="https://i.imgur.com/44d63g7.png",
            featured=[495, 498, 501],
        ),
        "kalos": RegionInfo(
            key="kalos",
            name="Kalos",
            pokedex="kalos-central",
            description="Estilo y emoción en cada rincón inspirado en la cultura francesa.",
            map_image="https://i.imgur.com/XpTyHge.png",
            featured=[650, 653, 656],
        ),
        "alola": RegionInfo(
            key="alola",
            name="Alola",
            pokedex="alola",
            description="Playas brillantes, tradiciones isleñas y muchas formas regionales.",
            map_image="https://i.imgur.com/HAMXlAf.png",
            featured=[722, 725, 728],
        ),
        "galar": RegionInfo(
            key="galar",
            name="Galar",
            pokedex="galar",
            description="Arenas deportivas y campos verdes donde los Pokémon se enfrentan con honor.",
            map_image="https://i.imgur.com/HxqnFPk.png",
            featured=[810, 813, 816],
        ),
        "paldea": RegionInfo(
            key="paldea",
            name="Paldea",
            pokedex="paldea",
            description="Academias, caminos libres y cafeterías llenas de entrenadores alegres.",
            map_image="https://i.imgur.com/qvdyduJ.png",
            featured=[906, 909, 912],
        ),
    }

    @classmethod
    def all(cls) -> List[RegionInfo]:
        return list(cls._REGIONS.values())

    @classmethod
    def get(cls, key: str) -> RegionInfo:
        normalized = (key or "").strip().lower()
        if normalized not in cls._REGIONS:
            raise KeyError(normalized)
        return cls._REGIONS[normalized]
