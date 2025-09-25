const searchForm = document.getElementById('search-form');
const searchInput = document.getElementById('search-input');
const randomButton = document.getElementById('random-button');
const messageBox = document.getElementById('message');
const card = document.getElementById('pokemon-card');
const nameEl = document.getElementById('pokemon-name');
const descEl = document.getElementById('pokemon-description');
const idEl = document.getElementById('pokemon-id');
const heightEl = document.getElementById('pokemon-height');
const weightEl = document.getElementById('pokemon-weight');
const imageEl = document.getElementById('pokemon-image');
const typesEl = document.getElementById('pokemon-types');
const abilitiesEl = document.getElementById('pokemon-abilities');
const statsEl = document.getElementById('pokemon-stats');
const typeSelect = document.getElementById('type-select');
const typeResults = document.getElementById('type-results');
const compareForm = document.getElementById('compare-form');
const compareAInput = document.getElementById('compare-a');
const compareBInput = document.getElementById('compare-b');
const compareMessage = document.getElementById('compare-message');
const compareResultsBox = document.getElementById('compare-results');
const compareWinner = document.getElementById('compare-winner');
const compareSummary = document.getElementById('compare-summary');

const compareElements = {
  a: {
    card: document.getElementById('compare-card-a'),
    image: document.getElementById('compare-a-image'),
    name: document.getElementById('compare-a-name'),
    total: document.getElementById('compare-a-total'),
    stats: document.getElementById('compare-a-stats'),
  },
  b: {
    card: document.getElementById('compare-card-b'),
    image: document.getElementById('compare-b-image'),
    name: document.getElementById('compare-b-name'),
    total: document.getElementById('compare-b-total'),
    stats: document.getElementById('compare-b-stats'),
  },
};

if (searchForm) {
  searchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const value = searchInput.value.trim();
    if (!value) {
      showMessage('Necesitamos que escribas algo antes de buscar.');
      return;
    }
    await loadPokemon(`/api/pokemon?q=${encodeURIComponent(value)}`);
  });
}

if (randomButton) {
  randomButton.addEventListener('click', async () => {
    await loadPokemon('/api/pokemon/random');
  });
}

if (typeSelect) {
  typeSelect.addEventListener('change', async () => {
    const value = typeSelect.value;
    typeResults.innerHTML = '';
    if (!value) {
      return;
    }

    renderTypeLoading();
    try {
      const response = await fetch(`/api/types/${value}`);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || 'Ocurrio un problema al cargar el tipo.');
      }
      renderTypeResults(payload.pokemon, payload.type);
    } catch (error) {
      renderTypeError(error.message);
    }
  });
}

if (compareForm) {
  compareForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const first = compareAInput.value.trim();
    const second = compareBInput.value.trim();

    if (!first || !second) {
      showCompareMessage('Necesitamos dos Pokémon para comparar.');
      return;
    }

    showCompareMessage('Preparando el combate...');
    try {
      const response = await fetch(
        `/api/pokemon/compare?a=${encodeURIComponent(first)}&b=${encodeURIComponent(second)}`
      );
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || 'No pudimos comparar a esos Pokémon.');
      }
      renderComparison(payload);
      showCompareMessage('');
      if (compareResultsBox) {
        compareResultsBox.hidden = false;
        compareResultsBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } catch (error) {
      showCompareMessage(error.message || 'Algo salió mal en la comparación.');
      if (compareResultsBox) {
        compareResultsBox.hidden = true;
      }
    }
  });
}

async function loadPokemon(endpoint) {
  showMessage('Cargando tu Pokemon...');
  try {
    const response = await fetch(endpoint);
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || 'No pudimos encontrar ese Pokemon.');
    }
    renderPokemon(payload);
    showMessage('');
  } catch (error) {
    showMessage(error.message || 'Vaya, algo salio mal.');
    card.hidden = true;
  }
}

function renderPokemon(data) {
  nameEl.textContent = data.name;
  descEl.textContent = data.description;
  idEl.textContent = `#${String(data.id).padStart(3, '0')}`;
  heightEl.textContent = `${data.height_m} m`;
  weightEl.textContent = `${data.weight_kg} kg`;
  imageEl.src =
    data.image_url ||
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/dream-ball.png';
  imageEl.alt = `Ilustracion de ${data.name}`;

  renderTagList(typesEl, data.types);
  renderTagList(abilitiesEl, data.abilities);

  statsEl.innerHTML = '';
  (data.stats || []).forEach((stat) => {
    const li = document.createElement('li');
    li.textContent = `${stat.name}: ${stat.value}`;
    statsEl.appendChild(li);
  });

  card.hidden = false;
}

function renderTagList(container, items) {
  container.innerHTML = '';
  (items || []).forEach((item) => {
    const span = document.createElement('span');
    span.textContent = item;
    container.appendChild(span);
  });
}

function showMessage(text) {
  messageBox.textContent = text;
}

function showCompareMessage(text) {
  if (compareMessage) {
    compareMessage.textContent = text;
  }
}

function renderTypeLoading() {
  typeResults.innerHTML = '<p class="loading">Cargando lista...</p>';
}

function renderTypeError(message) {
  typeResults.innerHTML = '';
  const errorBox = document.createElement('p');
  errorBox.className = 'error';
  errorBox.textContent = message;
  typeResults.appendChild(errorBox);
}

function renderTypeResults(list) {
  typeResults.innerHTML = '';
  if (!Array.isArray(list) || !list.length) {
    typeResults.innerHTML = '<p class="empty">No hay Pokemon para mostrar.</p>';
    return;
  }

  list.forEach((item) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = item.name;
    button.addEventListener('click', () => {
      loadPokemon(`/api/pokemon?q=${encodeURIComponent(item.id)}`);
      typeSelect.value = '';
    });
    typeResults.appendChild(button);
  });
}

function renderComparison(result) {
  if (!result || !Array.isArray(result.pokemon)) {
    throw new Error('Respuesta inesperada de la comparación.');
  }

  const [first, second] = result.pokemon;
  renderMiniCard(first, 'a', result);
  renderMiniCard(second, 'b', result);

  if (compareWinner && compareSummary) {
    if (result.is_tie) {
      compareWinner.textContent = '¡Empate de poder!';
    } else {
      compareWinner.textContent = `Ganador: ${result.winner}`;
    }
    compareSummary.textContent = result.message || '';
  }
}

function renderMiniCard(data, slot, result) {
  if (!data || !compareElements[slot]) {
    return;
  }

  const elements = compareElements[slot];
  const fallback =
    'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png';

  elements.image.src = data.image_url || fallback;
  elements.image.alt = `Retrato de ${data.name}`;
  elements.name.textContent = data.name || 'Desconocido';
  elements.total.textContent = data.total_stats ?? '0';

  const stats = Array.isArray(data.stats) ? data.stats.slice(0, 3) : [];
  elements.stats.innerHTML = '';
  stats.forEach((stat) => {
    const li = document.createElement('li');
    li.textContent = `${stat.name}: ${stat.value}`;
    elements.stats.appendChild(li);
  });

  const isWinner = Boolean(result && !result.is_tie && data.name === result.winner);
  elements.card.classList.toggle('mini-card--winner', isWinner);
}

// Carga inicial con un Pokemon al azar para animar a explorar.
loadPokemon('/api/pokemon/random');
