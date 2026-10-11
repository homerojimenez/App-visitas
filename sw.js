// Offline cache for the Segovia guide.
// Shell (page, map data, local MapLibre copy): precached at install, network-first with a 3 s timeout.
// Media (audio, photos): cache-first in a fixed cache; URLs carry ?v=<hash> so changed files get new keys.
// Range requests are answered from the cached file so audio plays offline on iOS Safari.
const V = 'sgv-v11';
const MEDIA = 'sgv-media';
const SHELL = ['index.html', 'map.json', 'lib/maplibre-gl.js', 'fonts/NotoReg/0-255.ttf', 'manifest.webmanifest', 'icon-180.png'];

self.addEventListener('install', e => {
  self.skipWaiting();
  e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).catch(() => {}));
});

self.addEventListener('activate', e => e.waitUntil((async () => {
  const keys = await caches.keys();
  await Promise.all(keys.filter(k => k.startsWith('sgv-') && k !== V && k !== MEDIA).map(k => caches.delete(k)));
  await self.clients.claim();
})()));

const isMedia = u => /\.(mp3|webp|png|jpg)$/.test(u.pathname) && u.origin === location.origin;

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const u = new URL(r.url);
  // Only handle our own files and the font/CDN hosts; live game traffic (ntfy.sh), weather and maps links pass through untouched.
  if (u.origin !== location.origin && !/gstatic\.com|googleapis\.com|unpkg\.com/.test(u.host)) return;
  const range = r.headers.get('range');

  if (range) {
    e.respondWith((async () => {
      const m = await caches.match(r.url);
      if (!m) {
        // Store the whole file in the background so the next play works offline.
        e.waitUntil(fetch(r.url).then(res => res.ok && caches.open(MEDIA).then(c => c.put(r.url, res))).catch(() => {}));
        return fetch(r);
      }
      const buf = await m.arrayBuffer();
      const g = /bytes=(\d+)-(\d*)/.exec(range) || [];
      const start = +g[1] || 0, end = g[2] ? Math.min(+g[2], buf.byteLength - 1) : buf.byteLength - 1;
      return new Response(buf.slice(start, end + 1), { status: 206, headers: {
        'Content-Range': `bytes ${start}-${end}/${buf.byteLength}`,
        'Content-Length': String(end - start + 1),
        'Content-Type': m.headers.get('Content-Type') || 'audio/mpeg',
        'Accept-Ranges': 'bytes' } });
    })());
    return;
  }

  const shell = r.mode === 'navigate' || /\.(html|json|webmanifest)$/.test(u.pathname) || u.pathname.endsWith('/');
  if (shell) {
    e.respondWith((async () => {
      const cached = (await caches.match(r, { cacheName: V, ignoreSearch: true })) ||
                     (r.mode === 'navigate' ? await caches.match('index.html', { cacheName: V, ignoreSearch: true }) : null);
      const net = fetch(r).then(res => {
        if (res.ok) { const c = res.clone(); caches.open(V).then(x => x.put(r, c)); }
        return res;
      });
      e.waitUntil(net.catch(() => {}));
      if (!cached) return net.catch(() => Response.error());
      // map.json: serve the cached copy at once and refresh it in the background.
      if (u.pathname.endsWith('map.json')) return cached;
      return Promise.race([net, new Promise(ok => setTimeout(() => ok(cached), 3000))]).catch(() => cached);
    })());
    return;
  }

  e.respondWith((async () => {
    const m = isMedia(u) ? await caches.match(r) : await caches.match(r, { ignoreSearch: true });
    if (m) return m;
    try {
      const res = await fetch(r);
      if (res.ok && (u.origin === location.origin || /unpkg\.com|gstatic\.com|googleapis\.com/.test(u.host))) {
        const c = res.clone();
        caches.open(isMedia(u) ? MEDIA : V).then(x => x.put(r, c));
      }
      return res;
    } catch (err) {
      return Response.error();
    }
  })());
});
