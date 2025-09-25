from __future__ import annotations

import requests

from .exceptions import PokeAPIError, PokemonNotFoundError


class PokeAPIClient:
    """HTTP client encapsulating interactions with the public PokéAPI."""

    BASE_URL = "https://pokeapi.co/api/v2"
    MAX_POKEMON_ID = 1010

    def __init__(self, session: requests.Session | None = None, timeout: int = 10) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout

    def _get(self, endpoint: str) -> dict:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(url, timeout=self.timeout)
        except requests.RequestException as exc:
            raise PokeAPIError(
                "No pudimos conectar con la PokéAPI. ¿Hay internet en tu Pokédex?"
            ) from exc

        if response.status_code == 404:
            raise PokemonNotFoundError("¡Oh no! Ese Pokémon no existe todavía.")

        if not response.ok:
            raise PokeAPIError(
                "La PokéAPI respondió con un error inesperado. Inténtalo de nuevo más tarde."
            )

        try:
            return response.json()
        except ValueError as exc:
            raise PokeAPIError("La PokéAPI envió datos que no pudimos entender.") from exc

    def get_pokemon(self, identifier: str | int) -> dict:
        return self._get(f"pokemon/{identifier}")

    def get_pokemon_species(self, identifier: str | int) -> dict:
        return self._get(f"pokemon-species/{identifier}")

    def get_type(self, type_name: str) -> dict:
        return self._get(f"type/{type_name}")
