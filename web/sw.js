const V = 'fr-v4';

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(V).then((c) => c.addAll(['./', './index.html']))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((ks) => Promise.all(
      ks.filter((k) => k !== V).map((k) => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const u = new URL(e.request.url);
  const isNav = e.request.mode === 'navigate';
  const isJson = u.pathname.endsWith('.json');
  if (!isNav && !isJson) return;
  e.respondWith(
    fetch(e.request).then((r) => {
      const c = r.clone();
      caches.open(V).then((cc) => cc.put(e.request, c));
      return r;
    }).catch(() => caches.match(e.request))
  );
});
