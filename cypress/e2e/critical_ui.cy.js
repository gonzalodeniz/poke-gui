const randomPokemon = {
  id: 25,
  name: 'Pikachu',
  description: 'El compañero eléctrico definitivo.',
  height_m: 0.4,
  weight_kg: 6.0,
  types: ['Electric'],
  abilities: ['Static'],
  stats: [
    { name: 'HP', value: 35 },
    { name: 'Attack', value: 55 },
    { name: 'Speed', value: 90 },
  ],
  image_url: 'https://img.example/pikachu.png',
  total_stats: 180,
};

const charmanderPokemon = {
  id: 4,
  name: 'Charmander',
  description: 'Lagartija de fuego que cuida su llama.',
  height_m: 0.6,
  weight_kg: 8.5,
  types: ['Fire'],
  abilities: ['Blaze'],
  stats: [
    { name: 'HP', value: 39 },
    { name: 'Attack', value: 52 },
    { name: 'Speed', value: 65 },
  ],
  image_url: 'https://img.example/charmander.png',
  total_stats: 156,
};

const comparePayload = {
  winner: 'Pikachu',
  is_tie: false,
  message: '¡Pikachu gana! Sus estadísticas superan a Charmander.',
  difference: 24,
  pokemon: [randomPokemon, charmanderPokemon],
};

const typeFirePayload = {
  type: 'Fire',
  pokemon: [
    { id: 4, name: 'Charmander' },
    { id: 6, name: 'Charizard' },
  ],
};

const regionsCataloguePayload = {
  regions: [
    {
      key: 'kanto',
      name: 'Kanto',
      description: 'El comienzo de toda aventura.',
      map_image: 'https://img.example/kanto-map.png',
      featured: [25, 1, 4],
    },
  ],
};

const regionDetailsPayload = {
  region: regionsCataloguePayload.regions[0],
  pokemon: [
    { id: 25, name: 'Pikachu' },
    { id: 4, name: 'Charmander' },
  ],
  total_available: 2,
};

const searchLookup = {
  charmander: charmanderPokemon,
  '4': charmanderPokemon,
  '25': randomPokemon,
};

const getSearchPayload = (query) => {
  const normalized = (query || '').toString().toLowerCase();
  return searchLookup[normalized] || randomPokemon;
};

describe('Mini Pokedex Aventurera - Flujos críticos con Cypress', () => {
  const APP_URL = Cypress.config('baseUrl') || 'http://localhost:5000';

  beforeEach(() => {
    cy.intercept('GET', '/api/pokemon/random', randomPokemon).as('randomPokemon');
    cy.intercept('GET', /\/api\/pokemon\?q=.*/, (req) => {
      const url = new URL(req.url);
      const query = url.searchParams.get('q');
      req.reply(getSearchPayload(query));
    }).as('searchPokemon');
    cy.intercept('GET', '/api/types/fire', typeFirePayload).as('typeFire');
    cy.intercept('GET', /\/api\/pokemon\/compare.*/, comparePayload).as('comparePokemon');
    cy.intercept('GET', '/api/regions', regionsCataloguePayload).as('regionsCatalogue');
    cy.intercept('GET', '/api/regions/kanto?limit=12', regionDetailsPayload).as('regionDetails');

    cy.visit(APP_URL);
    cy.wait('@randomPokemon');
    cy.wait('@regionsCatalogue');
    cy.wait('@regionDetails');
  });

  it('permite buscar un Pokémon puntual y muestra su ficha', () => {
    cy.get('#search-input').clear().type('charmander');
    cy.get('#search-form').submit();

    cy.wait('@searchPokemon').its('request.url').should('include', 'charmander');
    cy.get('#pokemon-card').should('be.visible');
    cy.get('#pokemon-name').should('contain.text', 'Charmander');
    cy.get('#pokemon-stats li').should('have.length.at.least', 1);
  });

  it('actualiza la tarjeta con el botón sorpresa', () => {
    cy.get('#random-button').click();
    cy.wait('@randomPokemon');

    cy.get('#pokemon-name').should('contain.text', 'Pikachu');
    cy.get('#message').should('have.text', '');
  });

  it('muestra listas rápidas al filtrar por tipo y permite elegir desde allí', () => {
    cy.get('#type-select').select('Fuego');
    cy.wait('@typeFire');

    cy.get('#type-results button').should('have.length', 2).first().should('contain.text', 'Charmander').click();
    cy.wait('@searchPokemon').its('request.url').should('include', 'q=4');
    cy.get('#pokemon-name').should('contain.text', 'Charmander');
  });

  it('resuelve duelos de estadísticas mostrando al ganador', () => {
    cy.get('#compare-a').type('pikachu');
    cy.get('#compare-b').type('charmander');
    cy.get('#compare-form').submit();

    cy.wait('@comparePokemon');
    cy.get('#compare-results').should('not.have.attr', 'hidden');
    cy.get('#compare-winner').should('contain.text', 'Pikachu');
    cy.get('#compare-summary').should('contain.text', 'gana');
  });

  it('carga el modo explorador de regiones y permite viajar', () => {
    cy.get('#region-select').find('option[value="kanto"]').should('exist');
    cy.get('#region-description').should('contain.text', 'El comienzo de toda aventura.');
    cy.get('#region-pokemon button').should('have.length', 2);
    cy.get('#region-icons img').should('have.length', 3);

    cy.get('#region-travel').click();
    cy.wait('@regionDetails');
    cy.get('#region-explorer-message').should('contain.text', 'Has viajado');
  });
});
