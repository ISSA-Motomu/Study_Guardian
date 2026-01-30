const CACHE_NAME = 'study-guardian-v4';

// インストール時：即座にアクティブ化
self.addEventListener('install', (event) => {
  console.log('[SW] Installing v4...');
  self.skipWaiting();
});

// アクティベート時：すべての古いキャッシュを削除
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating v4...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          console.log('[SW] Deleting old cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    })
  );
  // 即座に全クライアントをコントロール
  self.clients.claim();
});

// フェッチ：常にネットワーク優先（オフライン時のみキャッシュ使用）
self.addEventListener('fetch', (event) => {
  // APIとアセットは常にネットワークから
  if (event.request.url.includes('/api/') ||
    event.request.url.includes('/static/dist/')) {
    event.respondWith(
      fetch(event.request).catch(() => {
        // オフライン時はエラーを返す（キャッシュしない）
        return new Response('Offline', { status: 503 });
      })
    );
    return;
  }

  // その他のリクエスト：ネットワーク優先、失敗時はキャッシュ
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // 成功したらキャッシュに保存（HTMLのみ）
        if (response.status === 200 && event.request.mode === 'navigate') {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request);
      })
  );
});
