from __future__ import annotations

from flask import Blueprint, Flask, jsonify, render_template, request

from .exceptions import PokeAPIError, PokemonNotFoundError
from .pokemon_service import PokemonService


class PokemonController:
    """Registers HTTP endpoints that interact with the Pokémon service."""

    def __init__(self, service: PokemonService) -> None:
        self.service = service
        self.blueprint = Blueprint("pokemon", __name__)
        self._register_routes()

    def register(self, app: Flask) -> None:
        app.register_blueprint(self.blueprint)

    def _register_routes(self) -> None:
        self.blueprint.add_url_rule("/", view_func=self.home, methods=["GET"])
        self.blueprint.add_url_rule("/api/pokemon", view_func=self.search_pokemon, methods=["GET"])
        self.blueprint.add_url_rule(
            "/api/pokemon/random", view_func=self.random_pokemon, methods=["GET"]
        )
        self.blueprint.add_url_rule(
            "/api/types/<string:type_name>", view_func=self.pokemon_by_type, methods=["GET"]
        )
        self.blueprint.add_url_rule(
            "/api/pokemon/compare", view_func=self.compare_pokemon, methods=["GET"]
        )
        self.blueprint.add_url_rule(
            "/api/regions", view_func=self.regions_catalogue, methods=["GET"]
        )
        self.blueprint.add_url_rule(
            "/api/regions/<string:region_key>",
            view_func=self.region_details,
            methods=["GET"],
        )

    def home(self):
        return render_template("index.html")

    def search_pokemon(self):
        query = request.args.get("q", "").strip()
        if not query:
            return (
                jsonify({"error": "Por favor, escribe el nombre o número de un Pokémon."}),
                400,
            )
        try:
            pokemon = self.service.get_pokemon(query.lower())
        except PokemonNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except PokeAPIError as exc:
            return jsonify({"error": str(exc)}), 502
        return jsonify(pokemon.to_dict())

    def random_pokemon(self):
        try:
            pokemon = self.service.get_random_pokemon()
        except PokeAPIError as exc:
            return jsonify({"error": str(exc)}), 502
        return jsonify(pokemon.to_dict())

    def pokemon_by_type(self, type_name: str):
        try:
            summaries = self.service.get_pokemon_by_type(type_name.lower())
        except PokemonNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except PokeAPIError as exc:
            return jsonify({"error": str(exc)}), 502
        return jsonify({"type": type_name.title(), "pokemon": [s.to_dict() for s in summaries]})

    def compare_pokemon(self):
        first = request.args.get("a", "").strip()
        second = request.args.get("b", "").strip()

        if not first or not second:
            return (
                jsonify({"error": "Necesitamos dos Pokémon para hacer la comparación."}),
                400,
            )

        try:
            result = self.service.compare_pokemon(first, second)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except PokemonNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except PokeAPIError as exc:
            return jsonify({"error": str(exc)}), 502

        return jsonify(result)

    def regions_catalogue(self):
        regions = self.service.get_regions_catalogue()
        return jsonify({"regions": regions})

    def region_details(self, region_key: str):
        try:
            limit = int(request.args.get("limit", 12))
        except ValueError:
            limit = 12

        try:
            payload = self.service.get_region_details(region_key, limit=limit)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except PokemonNotFoundError as exc:
            return jsonify({"error": str(exc)}), 404
        except PokeAPIError as exc:
            return jsonify({"error": str(exc)}), 502

        return jsonify(payload)
