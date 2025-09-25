class PokemonNotFoundError(Exception):
    """Raised when a requested Pokémon cannot be found."""


class PokeAPIError(Exception):
    """Raised when the PokéAPI returns an unexpected error."""
