const SURUM = "anlikceviri-v1";
const DOSYALAR = ["./", "index.html", "gizlilik.html", "icon.svg", "icon-192.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(SURUM).then(c => c.addAll(DOSYALAR)).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== SURUM && x !== "paylasim").map(x => caches.delete(x))))); self.clients.claim(); });
self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  // Galeriden "Paylaş -> AnlıkÇeviri" ile gelen görüntü
  if (e.request.method === "POST" && url.pathname.endsWith("/paylas")) {
    e.respondWith((async () => {
      try {
        const fd = await e.request.formData();
        const f = fd.get("resim");
        if (f) { const c = await caches.open("paylasim"); await c.put(new URL("paylasilan", self.registration.scope).href, new Response(f)); }
      } catch (err) {}
      return Response.redirect(new URL("./?paylasildi=1", self.registration.scope).href, 303);
    })());
    return;
  }
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => { const k = r.clone(); caches.open(SURUM).then(c => c.put(e.request, k)); return r; }).catch(() => caches.match(e.request)));
});
