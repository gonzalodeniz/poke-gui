import pytest

from app.exceptions import PokemonNotFoundError
from app.models import PokemonSummary
from app.pokemon_service import PokemonService


class FakeClient:
    MAX_POKEMON_ID = 1010

    def __init__(self, pokemon_payload=None, species_payload=None, type_payload=None):
        self._pokemon_payload = pokemon_payload or {}
        self._species_payload = species_payload or {"flavor_text_entries": []}
        self._type_payload = type_payload or {"pokemon": []}
        self.requested_ids = []
        self.pokemon_overrides = {}

    def get_pokemon(self, identifier):
        self.requested_ids.append(identifier)
        key = str(identifier).strip().lower()
        if key in self.pokemon_overrides:
            return self.pokemon_overrides[key]
        return self._pokemon_payload

    def get_pokemon_species(self, identifier):
        return self._species_payload

    def get_type(self, type_name):
        if self._type_payload is None:
            raise PokemonNotFoundError("No type")
        return self._type_payload


class FixedRandom:
    def __init__(self, value):
        self.value = value

    def randint(self, *_args):
        return self.value


@pytest.fixture
def sample_pokemon_payload():
    return {
        "id": 7,
        "name": "squirtle",
        "height": 5,
        "weight": 90,
        "types": [{"type": {"name": "water"}}],
        "abilities": [{"ability": {"name": "torrent"}}],
        "stats": [{"stat": {"name": "hp"}, "base_stat": 44}],
        "sprites": {"front_default": "http://example.com/squirtle.png"},
    }


@pytest.fixture
def sample_species_payload():
    return {
        "flavor_text_entries": [
            {"language": {"name": "en"}, "flavor_text": "Loves swimming.\nAlways happy!"}
        ]
    }


@pytest.fixture
def sample_type_payload():
    return {
        "pokemon": [
            {"pokemon": {"name": "squirtle", "url": "https://pokeapi.co/api/v2/pokemon/7/"}},
            {"pokemon": {"name": "psyduck", "url": "https://pokeapi.co/api/v2/pokemon/54/"}},
        ]
    }


def test_get_pokemon_returns_domain_model(sample_pokemon_payload, sample_species_payload):
    client = FakeClient(sample_pokemon_payload, sample_species_payload)
    service = PokemonService(client=client)

    pokemon = service.get_pokemon("squirtle")

    assert pokemon.name == "Squirtle"
    assert "Always happy" in pokemon.description
    assert pokemon.types == ["Water"]


def test_get_random_pokemon_uses_rng(sample_pokemon_payload, sample_species_payload):
    client = FakeClient(sample_pokemon_payload, sample_species_payload)
    rng = FixedRandom(42)
    service = PokemonService(client=client, rng=rng)

    service.get_random_pokemon()

    assert client.requested_ids[0] == 42


def test_get_pokemon_by_type_returns_summaries(sample_type_payload):
    client = FakeClient(type_payload=sample_type_payload)
    service = PokemonService(client=client)

    results = service.get_pokemon_by_type("water")

    assert isinstance(results[0], PokemonSummary)
    assert results[0].identifier == 7
    assert results[0].name == "Squirtle"


def test_get_pokemon_by_type_raises_custom_message():
    client = FakeClient(type_payload={})
    client._type_payload = None
    service = PokemonService(client=client)

    with pytest.raises(PokemonNotFoundError) as exc:
        service.get_pokemon_by_type("mistery")

    assert "Revisa tu ort" in str(exc.value)


def test_compare_pokemon_selects_highest_total(sample_species_payload):
    client = FakeClient(species_payload=sample_species_payload)
    client.pokemon_overrides = {
        "pikachu": {
            "id": 25,
            "name": "pikachu",
            "height": 4,
            "weight": 60,
            "types": [{"type": {"name": "electric"}}],
            "abilities": [{"ability": {"name": "static"}}],
            "stats": [
                {"stat": {"name": "hp"}, "base_stat": 35},
                {"stat": {"name": "attack"}, "base_stat": 55},
                {"stat": {"name": "speed"}, "base_stat": 90},
            ],
            "sprites": {"front_default": "pikachu.png"},
        },
        "bulbasaur": {
            "id": 1,
            "name": "bulbasaur",
            "height": 7,
            "weight": 69,
            "types": [{"type": {"name": "grass"}}],
            "abilities": [{"ability": {"name": "overgrow"}}],
            "stats": [
                {"stat": {"name": "hp"}, "base_stat": 45},
                {"stat": {"name": "attack"}, "base_stat": 49},
                {"stat": {"name": "speed"}, "base_stat": 45},
            ],
            "sprites": {"front_default": "bulbasaur.png"},
        },
    }
    service = PokemonService(client=client)

    result = service.compare_pokemon("pikachu", "bulbasaur")

    assert result["winner"] == "Pikachu"
    assert not result["is_tie"]
    assert result["pokemon"][0]["total_stats"] == 180
    assert result["difference"] == 41


def test_compare_pokemon_handles_tie(sample_species_payload):
    base_entry = {
        "id": 4,
        "name": "charmander",
        "height": 6,
        "weight": 85,
        "types": [{"type": {"name": "fire"}}],
        "abilities": [{"ability": {"name": "blaze"}}],
        "stats": [
            {"stat": {"name": "hp"}, "base_stat": 39},
            {"stat": {"name": "attack"}, "base_stat": 52},
        ],
        "sprites": {"front_default": "charmander.png"},
    }
    client = FakeClient(species_payload=sample_species_payload)
    client.pokemon_overrides = {
        "charmander": base_entry,
        "vulpix": {**base_entry, "id": 37, "name": "vulpix"},
    }
    service = PokemonService(client=client)

    result = service.compare_pokemon("charmander", "vulpix")

    assert result["winner"] is None
    assert result["is_tie"]
    assert result["difference"] == 0


def test_compare_pokemon_requires_distinct_entries(sample_species_payload):
    client = FakeClient(species_payload=sample_species_payload)
    service = PokemonService(client=client)

    with pytest.raises(ValueError):
        service.compare_pokemon("pikachu", "pikachu")
