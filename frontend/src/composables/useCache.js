// composables/useCache.js
/**
 * LocalStorageキャッシュユーティリティ
 * 
 * 使い方:
 * const { getCache, setCache, clearCache } = useCache()
 * 
 * // データ保存（有効期限5分）
 * setCache('user_data', data, 5 * 60 * 1000)
 * 
 * // データ取得（期限切れならnull）
 * const data = getCache('user_data')
 */

const CACHE_PREFIX = 'sg_cache_'

export function useCache() {
  /**
   * キャッシュからデータを取得
   * @param {string} key キャッシュキー
   * @returns {any|null} キャッシュデータまたはnull（期限切れ・未存在時）
   */
  const getCache = (key) => {
    try {
      const raw = localStorage.getItem(CACHE_PREFIX + key)
      if (!raw) return null

      const cached = JSON.parse(raw)

      // 有効期限チェック
      if (cached.expiresAt && Date.now() > cached.expiresAt) {
        localStorage.removeItem(CACHE_PREFIX + key)
        return null
      }

      return cached.data
    } catch (e) {
      console.warn('Cache read error:', e)
      return null
    }
  }

  /**
   * キャッシュにデータを保存
   * @param {string} key キャッシュキー
   * @param {any} data 保存データ
   * @param {number} ttl 有効期限（ミリ秒）デフォルト5分
   */
  const setCache = (key, data, ttl = 5 * 60 * 1000) => {
    try {
      const cached = {
        data,
        expiresAt: Date.now() + ttl,
        cachedAt: Date.now()
      }
      localStorage.setItem(CACHE_PREFIX + key, JSON.stringify(cached))
    } catch (e) {
      console.warn('Cache write error:', e)
      // ストレージがいっぱいの場合、古いキャッシュを削除
      if (e.name === 'QuotaExceededError') {
        clearAllCache()
        try {
          localStorage.setItem(CACHE_PREFIX + key, JSON.stringify({ data, expiresAt: Date.now() + ttl }))
        } catch {
          // それでも失敗したら諦める
        }
      }
    }
  }

  /**
   * 特定のキャッシュを削除
   * @param {string} key キャッシュキー
   */
  const clearCache = (key) => {
    localStorage.removeItem(CACHE_PREFIX + key)
  }

  /**
   * 全てのStudy Guardianキャッシュを削除
   */
  const clearAllCache = () => {
    const keysToRemove = []
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i)
      if (key && key.startsWith(CACHE_PREFIX)) {
        keysToRemove.push(key)
      }
    }
    keysToRemove.forEach(k => localStorage.removeItem(k))
  }

  /**
   * キャッシュ付きfetch
   * キャッシュがあれば即座に返し、なければfetchしてキャッシュ
   * @param {string} key キャッシュキー
   * @param {Function} fetcher データ取得関数
   * @param {number} ttl 有効期限（ミリ秒）
   * @returns {Promise<any>}
   */
  const fetchWithCache = async (key, fetcher, ttl = 5 * 60 * 1000) => {
    // まずキャッシュ確認
    const cached = getCache(key)
    if (cached !== null) {
      return cached
    }

    // fetchしてキャッシュ
    const data = await fetcher()
    if (data !== null && data !== undefined) {
      setCache(key, data, ttl)
    }
    return data
  }

  return {
    getCache,
    setCache,
    clearCache,
    clearAllCache,
    fetchWithCache
  }
}

// キャッシュキー定数
export const CACHE_KEYS = {
  USER_DATA: (userId) => `user_${userId}`,
  ACTIVITY: 'global_activity',
  RANKINGS: 'rankings',
  MATERIALS: (userId) => `materials_${userId}`,
  SHOP_ITEMS: 'shop_items',
  JOBS: 'jobs',
}
