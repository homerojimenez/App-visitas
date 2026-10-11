// Offline cache for the Segovia guide: network-first for the page and map data,
// cache-first for media, with Range support so cached audio plays on iOS Safari.
const V = 'sgv-v5';
const MEDIA = 'sgv-media-v2';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil((async () => {
  const keys = await caches.keys();
  await Promise.all(keys.filter(k => k !== V && k !== MEDIA).map(k => caches.delete(k)));
  await self.clients.claim();
})()));

async function fromCache(req) {
  return (await caches.match(req, { ignoreSearch: true })) || (await caches.match(req.url, { ignoreSearch: true }));
}

self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const u = new URL(r.url);
  const range = r.headers.get('range');

  if (range) {
    e.respondWith((async () => {
      const m = await fromCache(r);
      if (!m) return fetch(r);
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

  const fresh = r.mode === 'navigate' || /\.(html|json)$/.test(u.pathname) || u.pathname.endsWith('/');
  if (fresh) {
    e.respondWith((async () => {
      try {
        const res = await fetch(r);
        if (res.ok) (await caches.open(V)).put(r, res.clone());
        return res;
      } catch (err) {
        return (await fromCache(r)) || (await caches.match('index.html', { ignoreSearch: true })) || Response.error();
      }
    })());
    return;
  }

  e.respondWith((async () => {
    const m = await fromCache(r);
    if (m) return m;
    try {
      const res = await fetch(r);
      if ((res.ok && u.origin === location.origin) || /unpkg\.com|gstatic\.com|googleapis\.com/.test(u.host)) {
        (await caches.open(V)).put(r, res.clone());
      }
      return res;
    } catch (err) {
      return Response.error();
    }
  })());
});
