from __future__ import annotations

import random
from typing import List

from .exceptions import PokeAPIError, PokemonNotFoundError
from .models import Pokemon, PokemonSummary
from .pokeapi_client import PokeAPIClient


class PokemonService:
    """Domain service that prepares friendly Pokémon data for the UI."""

    def __init__(self, client: PokeAPIClient, rng: random.Random | None = None) -> None:
        self.client = client
        self.rng = rng or random.Random()

    def get_pokemon(self, identifier: str | int) -> Pokemon:
        pokemon_data = self.client.get_pokemon(identifier)
        species_data = self.client.get_pokemon_species(pokemon_data.get("id"))
        description = self._extract_description(species_data)
        return Pokemon.from_api(pokemon_data, description)

    def get_random_pokemon(self) -> Pokemon:
        random_id = self.rng.randint(1, self.client.MAX_POKEMON_ID)
        return self.get_pokemon(random_id)

    def get_pokemon_by_type(self, type_name: str, limit: int = 12) -> List[PokemonSummary]:
        try:
            type_data = self.client.get_type(type_name)
        except PokemonNotFoundError as exc:
            raise PokemonNotFoundError(
                "No encontramos un tipo con ese nombre. ¡Revisa tu ortografía!"
            ) from exc
        summaries: List[PokemonSummary] = []
        for entry in type_data.get("pokemon", [])[:limit]:
            pokemon_info = entry.get("pokemon", {})
            summary = PokemonSummary.from_url(
                name=pokemon_info.get("name", ""),
                url=pokemon_info.get("url", ""),
            )
            summaries.append(summary)
        return summaries

    def compare_pokemon(self, identifier_a: str | int, identifier_b: str | int) -> dict:
        first_key = str(identifier_a).strip().lower()
        second_key = str(identifier_b).strip().lower()

        if not first_key or not second_key:
            raise ValueError("Necesitamos dos Pokémon para poder compararlos.")

        if first_key == second_key:
            raise ValueError("Debes elegir dos Pokémon distintos para la comparación.")

        first = self.get_pokemon(first_key)
        second = self.get_pokemon(second_key)

        score_first = first.total_stats
        score_second = second.total_stats

        winner: Pokemon | None
        if score_first > score_second:
            winner = first
            message = (
                f"¡{first.name} gana! Sus estadísticas suman {score_first} puntos superando a"
                f" {second.name}."
            )
        elif score_second > score_first:
            winner = second
            message = (
                f"¡{second.name} gana! Sus estadísticas suman {score_second} puntos superando a"
                f" {first.name}."
            )
        else:
            winner = None
            message = "¡Empate! Ambos Pokémon comparten la misma fuerza total."

        return {
            "winner": winner.name if winner else None,
            "is_tie": winner is None,
            "message": message,
            "difference": abs(score_first - score_second),
            "pokemon": [first.to_dict(), second.to_dict()],
        }

    def _extract_description(self, species_data: dict) -> str:
        entries = species_data.get("flavor_text_entries", [])
        for entry in entries:
            language = entry.get("language", {}).get("name")
            if language == "es":
                return self._clean_description(entry.get("flavor_text", ""))
        for entry in entries:
            language = entry.get("language", {}).get("name")
            if language == "en":
                return self._clean_description(entry.get("flavor_text", ""))
        return "Este Pokémon es todo un misterio. ¡Sigue investigando!"

    @staticmethod
    def _clean_description(text: str) -> str:
        cleaned = text.replace("\n", " ").replace("\f", " ")
        return " ".join(cleaned.split())
