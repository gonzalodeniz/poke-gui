from pathlib import Path

import pytest
from flask import Flask

pytest.importorskip("flask_testing")
from flask_testing import TestCase

from app.models import Pokemon, PokemonStat
from app.routes import PokemonController


BASE_DIR = Path(__file__).resolve().parents[1]


class ServiceDouble:
    def __init__(self):
        stats = [PokemonStat(name="HP", value=35), PokemonStat(name="Attack", value=55)]
        self.sample_pokemon = Pokemon(
            identifier=25,
            name="Pikachu",
            description="Un amigo electrizante.",
            height_m=0.4,
            weight_kg=6.0,
            types=["Electric"],
            abilities=["Static"],
            stats=stats,
            image_url="http://example.com/pikachu.png",
        )
        self.region_payload = {
            "key": "kanto",
            "name": "Kanto",
            "description": "Región inicial",
            "map_image": "http://example.com/map.png",
            "featured": [25, 1, 4],
        }

    def get_pokemon(self, _identifier):
        return self.sample_pokemon

    def get_random_pokemon(self):
        return self.sample_pokemon

    def get_pokemon_by_type(self, _type_name):
        return [{"id": 25, "name": "Pikachu"}]

    def compare_pokemon(self, _first, _second):
        return {
            "winner": "Pikachu",
            "is_tie": False,
            "message": "¡Pikachu gana!",
            "difference": 10,
            "pokemon": [self.sample_pokemon.to_dict(), self.sample_pokemon.to_dict()],
        }

    def get_regions_catalogue(self):
        return [self.region_payload]

    def get_region_details(self, region_key, limit=12):
        return {
            "region": self.region_payload,
            "pokemon": [{"id": 25, "name": "Pikachu"}],
            "total_available": 1,
            "limit": limit,
            "requested": region_key,
        }


class PokemonApiIntegrationTest(TestCase):
    def create_app(self):
        self.service = ServiceDouble()
        app = Flask(
            __name__,
            template_folder=str(BASE_DIR / "templates"),
            static_folder=str(BASE_DIR / "static"),
        )
        PokemonController(self.service).register(app)
        app.config["TESTING"] = True
        return app

    def test_search_endpoint_returns_valid_json(self):
        response = self.client.get("/api/pokemon", query_string={"q": "pikachu"})
        data = response.get_json()

        assert response.status_code == 200
        assert data["name"] == "Pikachu"
        assert data["stats"][0]["name"] == "HP"

    def test_random_endpoint_returns_valid_json(self):
        response = self.client.get("/api/pokemon/random")
        data = response.get_json()

        assert response.status_code == 200
        assert data["id"] == 25

    def test_regions_endpoint_returns_valid_json(self):
        response = self.client.get("/api/regions")
        data = response.get_json()

        assert response.status_code == 200
        assert data["regions"][0]["key"] == "kanto"
