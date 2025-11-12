# Mini Pokédex Aventurera

Aplicación web pensada para niños y niñas que quieran descubrir información del mundo Pokémon de una forma visual y sencilla. El sitio se apoya en Flask para servir contenido dinámico y consulta la [PokéAPI](https://pokeapi.co/) para obtener los datos oficiales.

## Características principales
- Búsqueda por nombre o número de Pokédex.
- Descubrimiento de Pokémon por tipo elemental con lista rápida.
- Botón sorpresa para mostrar un Pokémon aleatorio.
- Comparador de dos Pokémon que elige al ganador según las estadísticas totales.
- Modo explorador de regiones con mapas ilustrados e interacciones para viajar entre zonas.
- Tarjetas coloridas con descripción, tipos, habilidades y estadísticas básicas.
- Arquitectura orientada a objetos con clases para cliente, servicio, modelos y controlador.
- Conjunto de pruebas unitarias con `pytest` que cubren todas las clases.

## Requisitos mínimos
- Python 3.10 o superior.
- pip (gestor de paquetes).
- Acceso a Internet para consultar la PokéAPI durante la ejecución de la aplicación.

## Instalación en un servidor local
1. Clona o copia este directorio en tu servidor Linux (probado en Ubuntu 24.04).
2. Crea y activa un entorno virtual:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
4. Ejecuta la aplicación Flask:
   ```bash
   python run.py
   ```
5. Abre tu navegador y visita `http://localhost:5000` para explorar la mini Pokédex.

## Preparar el entorno de pruebas
1. Asegúrate de tener Python 3.10+, pip y Node.js (con npm).  
2. Ejecuta el script de preparación (instala dependencias Python y JavaScript, y garantiza la estructura de tests):
   ```bash
   chmod +x setup_tests.sh
   ./setup_tests.sh
   ```
   - Si tu entorno no tiene `npm`, instálalo antes de volver a ejecutar el script.

## Ejecutar pruebas
Puedes ejecutar cada suite por separado o lanzar todas de una sola vez.

### Pruebas unitarias (servicio/modelos)
```bash
pytest tests/test_models.py tests/test_pokeapi_client.py tests/test_pokemon_service.py tests/test_critical_features.py
```

### Pruebas de integración (rutas y controller)
```bash
pytest tests/test_routes.py tests/test_integration_api.py
```

### Pruebas de interfaz (E2E con Cypress)
1. Asegúrate de que la app Flask esté corriendo en `http://localhost:5000`:
   ```bash
   python run.py
   ```
2. En otra terminal:
   ```bash
   npx cypress run --e2e
   # o npx cypress open --e2e para modo interactivo
   ```

### Ejecutar todo automáticamente
Se incluye un script que orquesta las tres suites, levantando el servidor para Cypress de forma temporal:
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```
El script muestra un resumen final indicando qué bloque (unitarias, integración, interfaz) pasó o falló.

## Estructura del proyecto
```
pokemon_kids_app/
├── app/
│   ├── __init__.py          # Fábrica de la aplicación Flask.
│   ├── exceptions.py        # Excepciones específicas de dominio.
│   ├── models.py            # Modelos de datos y utilidades de transformación.
│   ├── pokeapi_client.py    # Cliente HTTP para interactuar con PokéAPI.
│   ├── pokemon_service.py   # Lógica de negocio y enriquecimiento de datos.
│   └── routes.py            # Controlador (blueprint) con los endpoints web.
├── static/
│   ├── css/style.css        # Estilos con estética infantil.
│   └── js/app.js            # Lógica de interacción en el navegador.
├── templates/
│   └── index.html           # Página principal con la interfaz de usuario.
├── tests/                   # Pruebas unitarias con pytest.
├── requirements.txt         # Dependencias del proyecto.
├── run.py                   # Punto de entrada para ejecutar el servidor.
└── README.md
```

## Notas adicionales
- El cliente HTTP maneja errores comunes (falta de conexión, recursos inexistentes, estados inválidos) para mostrar mensajes amigables a los niños.
- Aunque la aplicación funciona sin credenciales, respeta los límites de la PokéAPI evitando peticiones innecesarias y reutilizando la misma sesión HTTP.
- Puedes desactivar el modo debug en `run.py` para despliegues de producción.
