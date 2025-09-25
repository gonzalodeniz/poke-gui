from types import SimpleNamespace

import pytest
import requests

from app.exceptions import PokeAPIError, PokemonNotFoundError
from app.pokeapi_client import PokeAPIClient


class DummyResponse:
    def __init__(self, status_code=200, payload=None, ok=True, json_error=False):
        self.status_code = status_code
        self._payload = payload or {}
        self.ok = ok
        self._json_error = json_error

    def json(self):
        if self._json_error:
            raise ValueError("broken json")
        return self._payload


class DummySession:
    def __init__(self, response=None, error=None):
        self.response = response or DummyResponse()
        self.error = error
        self.calls = []

    def get(self, url, timeout):
        self.calls.append(SimpleNamespace(url=url, timeout=timeout))
        if self.error:
            raise self.error
        return self.response


def test_get_pokemon_returns_payload():
    payload = {"name": "pikachu"}
    session = DummySession(response=DummyResponse(200, payload, ok=True))
    client = PokeAPIClient(session=session)

    result = client.get_pokemon("pikachu")

    assert result == payload
    assert session.calls[0].url.endswith("pokemon/pikachu")


def test_get_pokemon_raises_not_found():
    session = DummySession(response=DummyResponse(404, ok=False))
    client = PokeAPIClient(session=session)

    with pytest.raises(PokemonNotFoundError):
        client.get_pokemon("missingno")


def test_get_pokemon_raises_error_on_bad_status():
    session = DummySession(response=DummyResponse(500, ok=False))
    client = PokeAPIClient(session=session)

    with pytest.raises(PokeAPIError):
        client.get_pokemon("pikachu")


def test_get_pokemon_raises_error_on_invalid_json():
    session = DummySession(response=DummyResponse(200, ok=True, json_error=True))
    client = PokeAPIClient(session=session)

    with pytest.raises(PokeAPIError):
        client.get_pokemon("pikachu")


def test_get_pokemon_raises_error_on_network_issue():
    session = DummySession(error=requests.RequestException("boom"))
    client = PokeAPIClient(session=session)

    with pytest.raises(PokeAPIError):
        client.get_pokemon("pikachu")


def test_get_pokedex_fetches_entries():
    payload = {"pokemon_entries": []}
    session = DummySession(response=DummyResponse(200, payload, ok=True))
    client = PokeAPIClient(session=session)

    result = client.get_pokedex("kanto")

    assert result == payload
    assert session.calls[0].url.endswith("pokedex/kanto")
