/* Salderingscheck service worker: offline werken, altijd eerst de nieuwste versie proberen */
var CACHE = 'salderingscheck-v23';
var BESTANDEN = ['/', '/index.html', '/calc.js', '/app.js', '/manifest.webmanifest', '/icons/icon.svg', '/icons/icon-192.png', '/icons/icon-512.png'];
self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(BESTANDEN); }).then(function () { return self.skipWaiting(); }));
});
self.addEventListener('activate', function (e) {
  e.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener('fetch', function (e) {
  var req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(fetch(req).then(function (res) {
    var kopie = res.clone();
    caches.open(CACHE).then(function (c) { c.put(req, kopie); });
    return res;
  }).catch(function () {
    return caches.match(req, { ignoreSearch: true }).then(function (r) { return r || caches.match('/'); });
  }));
});
