import pytest

from app.models import Pokemon, PokemonStat, PokemonSummary


@pytest.fixture
def pokemon_payload():
    return {
        "id": 25,
        "name": "pikachu",
        "height": 4,
        "weight": 60,
        "types": [{"type": {"name": "electric"}}],
        "abilities": [
            {"ability": {"name": "static"}},
            {"ability": {"name": "lightning-rod"}},
        ],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 35},
            {"stat": {"name": "attack"}, "base_stat": 55},
        ],
        "sprites": {
            "front_default": "https://img.pokemondb.net/sprites/pikachu.png",
            "other": {
                "official-artwork": {
                    "front_default": "https://img.pokemondb.net/artwork/pikachu.jpg"
                }
            },
        },
    }


@pytest.fixture
def pokemon_species_payload():
    return {
        "flavor_text_entries": [
            {
                "language": {"name": "es"},
                "flavor_text": "Cuando se enfada, este Pokemon lanza rayos desde las mejillas.",
            }
        ]
    }


def test_pokemon_stat_from_api_creates_readable_name():
    stat = PokemonStat.from_api({"stat": {"name": "special-attack"}, "base_stat": 90})
    assert stat.name == "Special Attack"
    assert stat.value == 90


def test_pokemon_from_api_builds_expected_model(pokemon_payload, pokemon_species_payload):
    pokemon = Pokemon.from_api(pokemon_payload, "Una descripcion electrica.")

    assert pokemon.identifier == 25
    assert pokemon.name == "Pikachu"
    assert pokemon.height_m == pytest.approx(0.4)
    assert pokemon.weight_kg == pytest.approx(6.0)
    assert pokemon.types == ["Electric"]
    assert pokemon.abilities == ["Static", "Lightning Rod"]
    assert pokemon.stats[0].to_dict() == {"name": "Hp", "value": 35}
    assert pokemon.image_url.endswith("pikachu.jpg")
    assert pokemon.description == "Una descripcion electrica."
    assert pokemon.total_stats == 90


def test_pokemon_to_dict_matches_expected_structure(pokemon_payload):
    pokemon = Pokemon.from_api(pokemon_payload, "Descripcion")
    data = pokemon.to_dict()

    assert data["id"] == 25
    assert data["types"] == ["Electric"]
    assert isinstance(data["stats"], list)
    assert data["stats"][0] == {"name": "Hp", "value": 35}
    assert data["total_stats"] == 90


def test_pokemon_summary_from_url_extracts_identifier():
    summary = PokemonSummary.from_url(
        "charmander", "https://pokeapi.co/api/v2/pokemon/4/"
    )
    assert summary.identifier == 4
    assert summary.name == "Charmander"
    assert summary.to_dict() == {"id": 4, "name": "Charmander"}


def test_pokemon_summary_handles_invalid_url_gracefully():
    summary = PokemonSummary.from_url("missing", "not-a-valid-url")
    assert summary.identifier == 0
    assert summary.name == "Missing"
