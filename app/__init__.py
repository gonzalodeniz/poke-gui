from __future__ import annotations

from pathlib import Path

from flask import Flask

from .pokeapi_client import PokeAPIClient
from .pokemon_service import PokemonService
from .routes import PokemonController


BASE_DIR = Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    client = PokeAPIClient()
    service = PokemonService(client=client)
    controller = PokemonController(service=service)
    controller.register(app)

    return app
