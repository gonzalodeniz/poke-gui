import copy
from unittest.mock import MagicMock

import pytest

from app.exceptions import PokeAPIError, PokemonNotFoundError
from app.models import Pokemon, PokemonStat
from app.pokemon_service import PokemonService


class FixedRandom:
    def __init__(self, value: int) -> None:
        self.value = value

    def randint(self, *_args) -> int:
        return self.value


def pokemon_payload(**overrides):
    payload = {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "types": [{"type": {"name": "electric"}}],
        "abilities": [{"ability": {"name": "static"}}],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 35},
            {"stat": {"name": "attack"}, "base_stat": 55},
        ],
        "sprites": {
            "other": {"official-artwork": {"front_default": "https://img/pika.png"}},
            "front_default": "https://img/pika-default.png",
        },
    }
    payload.update(overrides)
    return copy.deepcopy(payload)


def species_payload(entries=None):
    if entries is None:
        entries = [
            {"language": {"name": "es"}, "flavor_text": "Un Pokémon muy amistoso.\nSiempre atento."}
        ]
    return {"flavor_text_entries": copy.deepcopy(entries)}


def make_service(client=None, rng=None):
    client = client or MagicMock()
    client.MAX_POKEMON_ID = getattr(client, "MAX_POKEMON_ID", 1010)
    rng = rng or FixedRandom(25)
    return PokemonService(client=client, rng=rng), client


def test_get_pokemon_successfully_builds_domain_model():
    service, client = make_service()
    client.get_pokemon.return_value = pokemon_payload()
    client.get_pokemon_species.return_value = species_payload()

    pokemon = service.get_pokemon("pikachu")

    assert pokemon.name == "Pikachu"
    assert pokemon.description.startswith("Un Pokémon muy amistoso")
    assert pokemon.image_url.endswith("pika.png")
    client.get_pokemon.assert_called_once_with("pikachu")


def test_get_pokemon_propagates_not_found_error():
    service, client = make_service()
    client.get_pokemon.side_effect = PokemonNotFoundError("sin registro")

    with pytest.raises(PokemonNotFoundError):
        service.get_pokemon("missing")


def test_get_pokemon_falls_back_to_default_description():
    service, client = make_service()
    client.get_pokemon.return_value = pokemon_payload()
    client.get_pokemon_species.return_value = species_payload(entries=[])

    pokemon = service.get_pokemon("pikachu")

    assert "todo un misterio" in pokemon.description


def test_get_random_pokemon_uses_rng_boundaries():
    client = MagicMock()
    client.MAX_POKEMON_ID = 1010
    client.get_pokemon.return_value = pokemon_payload(id=1010)
    client.get_pokemon_species.return_value = species_payload()
    rng = FixedRandom(1010)
    service = PokemonService(client=client, rng=rng)

    result = service.get_random_pokemon()

    assert result.identifier == 1010
    client.get_pokemon.assert_called_once_with(1010)


def test_get_random_pokemon_surfaces_api_errors():
    service, client = make_service()
    client.get_pokemon.side_effect = PokeAPIError("sin conexión")

    with pytest.raises(PokeAPIError):
        service.get_random_pokemon()


def test_get_pokemon_by_type_limits_results():
    service, client = make_service()
    client.get_type.return_value = {
        "pokemon": [
            {"pokemon": {"name": "pikachu", "url": "https://pokeapi.co/api/v2/pokemon/25/"}},
            {"pokemon": {"name": "raichu", "url": "https://pokeapi.co/api/v2/pokemon/26/"}},
            {"pokemon": {"name": "pichu", "url": "https://pokeapi.co/api/v2/pokemon/172/"}},
        ]
    }

    summaries = service.get_pokemon_by_type("electric", limit=2)

    assert len(summaries) == 2
    assert summaries[0].name == "Pikachu"
    assert summaries[1].identifier == 26


def test_get_pokemon_by_type_rewrites_not_found_message():
    service, client = make_service()
    client.get_type.side_effect = PokemonNotFoundError("raw message")

    with pytest.raises(PokemonNotFoundError) as exc:
        service.get_pokemon_by_type("misterio")

    assert "Revisa tu ortografía" in str(exc.value)


def test_get_pokemon_by_type_accepts_zero_limit():
    service, client = make_service()
    client.get_type.return_value = {"pokemon": [{"pokemon": {"name": "pikachu", "url": "x"}}]}

    summaries = service.get_pokemon_by_type("electric", limit=0)

    assert summaries == []


def build_pokemon(name: str, total: int) -> Pokemon:
    return Pokemon(
        identifier=1,
        name=name,
        description=f"{name} description",
        height_m=0.7,
        weight_kg=6.9,
        types=["Electric"],
        abilities=["Static"],
        stats=[PokemonStat(name="Total", value=total)],
        image_url="https://img/pokemon.png",
    )


def test_compare_pokemon_returns_winner_message():
    service, _ = make_service()
    first = build_pokemon("Pikachu", 180)
    second = build_pokemon("Bulbasaur", 140)
    service.get_pokemon = MagicMock(side_effect=[first, second])

    result = service.compare_pokemon("pikachu", "bulbasaur")

    assert result["winner"] == "Pikachu"
    assert not result["is_tie"]
    assert result["difference"] == 40


def test_compare_pokemon_detects_same_identifier():
    service, _ = make_service()

    with pytest.raises(ValueError):
        service.compare_pokemon("pikachu", "pikachu")


def test_compare_pokemon_handles_ties():
    service, _ = make_service()
    one = build_pokemon("Charmander", 150)
    two = build_pokemon("Cyndaquil", 150)
    service.get_pokemon = MagicMock(side_effect=[one, two])

    result = service.compare_pokemon("charmander", "cyndaquil")

    assert result["winner"] is None
    assert result["is_tie"]
    assert result["difference"] == 0


def test_regions_catalogue_includes_featured_sets():
    service, _ = make_service()

    regions = service.get_regions_catalogue()

    assert any(region["key"] == "kanto" for region in regions)
    assert all("featured" in region for region in regions)


def test_region_details_returns_payload_with_limit():
    client = MagicMock()
    client.MAX_POKEMON_ID = 1010
    client.get_pokedex.return_value = {
        "pokemon_entries": [
            {
                "pokemon_species": {
                    "name": "bulbasaur",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/1/",
                }
            },
            {
                "pokemon_species": {
                    "name": "charmander",
                    "url": "https://pokeapi.co/api/v2/pokemon-species/4/",
                }
            },
        ]
    }
    service = PokemonService(client=client)

    payload = service.get_region_details("kanto", limit=1)

    assert payload["region"]["key"] == "kanto"
    assert payload["total_available"] == 2
    assert len(payload["pokemon"]) == 1
    assert payload["pokemon"][0]["name"] == "Bulbasaur"
    client.get_pokedex.assert_called_once_with("kanto")


def test_region_details_invalid_key_raises_value_error():
    service, _ = make_service()

    with pytest.raises(ValueError):
        service.get_region_details("ultra-space")
