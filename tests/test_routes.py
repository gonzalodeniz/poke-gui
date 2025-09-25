from pathlib import Path

import pytest
from flask import Flask

from app.exceptions import PokeAPIError, PokemonNotFoundError
from app.models import PokemonSummary
from app.routes import PokemonController


class DummyPokemon:
    def __init__(self, payload):
        self._payload = payload

    def to_dict(self):
        return self._payload


class ServiceStub:
    def __init__(self):
        self.pokemon_payload = {
            "id": 25,
            "name": "Pikachu",
            "description": "Un amigo electrico.",
            "height_m": 0.4,
            "weight_kg": 6.0,
            "types": ["Electric"],
            "abilities": ["Static"],
            "stats": [{"name": "Hp", "value": 35}],
            "image_url": "http://example.com/pikachu.png",
            "total_stats": 200,
        }
        self.random_payload = {
            "id": 4,
            "name": "Charmander",
            "description": "Una llama amigable.",
            "height_m": 0.6,
            "weight_kg": 8.5,
            "types": ["Fire"],
            "abilities": ["Blaze"],
            "stats": [{"name": "Attack", "value": 52}],
            "image_url": "http://example.com/charmander.png",
            "total_stats": 150,
        }
        self.type_payload = [PokemonSummary(identifier=25, name="Pikachu")]
        self.raise_on_get = None
        self.raise_on_random = None
        self.raise_on_type = None
        self.raise_on_compare = None
        self.last_query = None
        self.last_type = None
        self.last_compare = None
        self.compare_payload = {
            "winner": "Pikachu",
            "is_tie": False,
            "message": "¡Pikachu gana la batalla de estadísticas!",
            "difference": 50,
            "pokemon": [self.pokemon_payload, self.random_payload],
        }

    def get_pokemon(self, identifier):
        self.last_query = identifier
        if self.raise_on_get:
            raise self.raise_on_get
        return DummyPokemon(self.pokemon_payload)

    def get_random_pokemon(self):
        if self.raise_on_random:
            raise self.raise_on_random
        return DummyPokemon(self.random_payload)

    def get_pokemon_by_type(self, type_name):
        self.last_type = type_name
        if self.raise_on_type:
            raise self.raise_on_type
        return self.type_payload

    def compare_pokemon(self, first, second):
        self.last_compare = (first, second)
        if self.raise_on_compare:
            raise self.raise_on_compare
        return self.compare_payload


@pytest.fixture
def flask_client():
    base_dir = Path(__file__).resolve().parents[1]
    service = ServiceStub()
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    PokemonController(service).register(app)
    app.testing = True
    return app.test_client(), service


def test_home_route_renders_template(flask_client):
    client, _ = flask_client
    response = client.get("/")
    assert response.status_code == 200
    assert "Mini Pokedex Aventurera" in response.get_data(as_text=True)


def test_search_pokemon_returns_json(flask_client):
    client, service = flask_client
    response = client.get("/api/pokemon", query_string={"q": "pikachu"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 25
    assert service.last_query == "pikachu"


def test_search_pokemon_handles_missing_query(flask_client):
    client, _ = flask_client
    response = client.get("/api/pokemon")
    assert response.status_code == 400


def test_search_pokemon_handles_not_found(flask_client):
    client, service = flask_client
    service.raise_on_get = PokemonNotFoundError("No existe")

    response = client.get("/api/pokemon", query_string={"q": "unknown"})
    data = response.get_json()

    assert response.status_code == 404
    assert "No existe" in data["error"]


def test_random_pokemon_endpoint(flask_client):
    client, _ = flask_client
    response = client.get("/api/pokemon/random")
    data = response.get_json()

    assert response.status_code == 200
    assert data["name"] == "Charmander"


def test_random_pokemon_handles_error(flask_client):
    client, service = flask_client
    service.raise_on_random = PokeAPIError("API sin respuesta")

    response = client.get("/api/pokemon/random")
    assert response.status_code == 502


def test_type_endpoint_returns_list(flask_client):
    client, service = flask_client
    response = client.get("/api/types/electric")
    data = response.get_json()

    assert response.status_code == 200
    assert data["pokemon"][0]["id"] == 25
    assert service.last_type == "electric"


def test_type_endpoint_handles_not_found(flask_client):
    client, service = flask_client
    service.raise_on_type = PokemonNotFoundError("Sin resultados")

    response = client.get("/api/types/fake")
    assert response.status_code == 404


def test_type_endpoint_handles_error(flask_client):
    client, service = flask_client
    service.raise_on_type = PokeAPIError("Fallo externo")

    response = client.get("/api/types/fail")
    assert response.status_code == 502


def test_compare_endpoint_returns_result(flask_client):
    client, service = flask_client
    response = client.get(
        "/api/pokemon/compare", query_string={"a": "pikachu", "b": "charmander"}
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["winner"] == "Pikachu"
    assert service.last_compare == ("pikachu", "charmander")


def test_compare_endpoint_requires_both_params(flask_client):
    client, _ = flask_client
    response = client.get("/api/pokemon/compare", query_string={"a": "pikachu"})
    assert response.status_code == 400


def test_compare_endpoint_handles_value_error(flask_client):
    client, service = flask_client
    service.raise_on_compare = ValueError("Repite otro contrincante")

    response = client.get(
        "/api/pokemon/compare", query_string={"a": "pikachu", "b": "pikachu"}
    )
    data = response.get_json()

    assert response.status_code == 400
    assert "Repite" in data["error"]


def test_compare_endpoint_handles_not_found(flask_client):
    client, service = flask_client
    service.raise_on_compare = PokemonNotFoundError("Sin registro")

    response = client.get(
        "/api/pokemon/compare", query_string={"a": "pikachu", "b": "missing"}
    )
    assert response.status_code == 404


def test_compare_endpoint_handles_api_error(flask_client):
    client, service = flask_client
    service.raise_on_compare = PokeAPIError("No responde")

    response = client.get(
        "/api/pokemon/compare", query_string={"a": "pikachu", "b": "mew"}
    )
    assert response.status_code == 502
