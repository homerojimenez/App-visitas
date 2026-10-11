# Segovia a pie

Guía de un día por Segovia (domingo 11 de octubre): de la estación de Guiomar al Acueducto en bus, a pie hasta el Alcázar y vuelta al tren.

**Abrir en el móvil (con GPS):** https://raw.githack.com/homerojimenez/App-visitas/HEAD/index.html

## Qué incluye

- Mapa vectorial con calles y edificios reales (Overture Maps / OpenStreetMap), la ruta a pie calculada sobre las calles y el trayecto del bus 11 hasta la estación.
- Ubicación en directo: punto azul, distancia y minutos a la parada actual y a la siguiente, aviso al llegar y modo seguimiento.
- 14 paradas, incluidas la llegada y la salida de la estación, con 13 audioguías narradas con ElevenLabs, fotos actuales e históricas y comparadores antes/después.
- Horarios de domingo del bus 11 según Moovit, con cuenta atrás hasta la próxima salida.
- Indicador de ritmo (adelantados o tarde respecto al plan) con un atajo propuesto en cada parada.
- Plan del día, tiempo en directo (Open-Meteo), pasaporte de paradas y modo sin cobertura (service worker).

## Archivos

- `index.html`: la app web completa.
- `artifact.html`: la misma app para el artifact de claude.ai (sin GPS; enlaza a la versión web).
- `sw.js`: caché sin conexión.
- `map.json`, `fonts/`: datos y tipografía del mapa.
- `audio/`, `img/`: audioguías y fotos (Wikimedia Commons).
- `tools/`: scripts que extraen el mapa, calculan las rutas y generan los HTML (`python3 tools/build.py`).

Los horarios de bus, monumentos y trenes son orientativos: comprobadlos el mismo día.
