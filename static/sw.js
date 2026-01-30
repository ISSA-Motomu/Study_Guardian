const CACHE_NAME = 'study-guardian-v3';
const urlsToCache = [
  '/app/dashboard',
  '/static/dist/index.html',
  '/static/manifest.json'
];

// 古いキャッシュバージョンのリスト（これらを削除する）
const OLD_CACHES = ['study-guardian-v1', 'study-guardian-v2'];

// インストール時にキャッシュ
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch((err) => {
        console.log('Cache failed:', err);
      })
  );
  // 即座にアクティブ化
  self.skipWaiting();
});

// アクティベート時に古いキャッシュを削除
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // 即座にコントロール
  self.clients.claim();
});

// フェッチ時にネットワークファースト、フォールバックでキャッシュ
self.addEventListener('fetch', (event) => {
  // APIリクエストはキャッシュしない
  if (event.request.url.includes('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // JSとCSSファイルは常にネットワークから取得（ハッシュ付きファイル）
  if (event.request.url.includes('/static/dist/assets/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // 成功したらキャッシュに保存
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // オフライン時はキャッシュから
        return caches.match(event.request);
      })
  );
});
