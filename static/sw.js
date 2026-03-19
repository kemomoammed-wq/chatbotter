// Service Worker لدعم PWA وإشعارات Push
self.addEventListener('install', (event) => {
  // تثبيت Service Worker وتخزين الملفات في Cache
  event.waitUntil(
    caches.open('chatbot-cache').then((cache) => {
      return cache.addAll([
        '/',
        '/static/styles/styles.css',
        '/static/js/scripts.js',
        '/room'
      ]);
    })
  );
});

self.addEventListener('fetch', (event) => {
  // التعامل مع طلبات الشبكة مع دعم Offline
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});

self.addEventListener('push', (event) => {
  // عرض إشعارات Push
  const data = event.data.text();
  event.waitUntil(
    self.registration.showNotification('رسالة جديدة', {
      body: data,
      icon: '/static/icon-192.png'
    })
  );
});