/**
 * API呼び出し用ユーティリティ
 * 429エラーなどを共通でハンドリング
 */
import { useToastStore } from '@/stores/toast'

let rateLimitShownAt = 0
const RATE_LIMIT_COOLDOWN = 10000 // 10秒間は同じエラーを表示しない

/**
 * API呼び出し（429エラーを自動ハンドリング）
 * @param {string} url - APIのURL
 * @param {RequestInit} options - fetchオプション
 * @returns {Promise<Response>}
 */
export async function apiCall(url, options = {}) {
  const response = await fetch(url, options)

  if (response.status === 429) {
    handleRateLimitError()
    throw new Error('Rate limit exceeded')
  }

  return response
}

/**
 * JSONを返すAPI呼び出し
 * @param {string} url - APIのURL
 * @param {RequestInit} options - fetchオプション
 * @returns {Promise<any>}
 */
export async function apiJson(url, options = {}) {
  const response = await apiCall(url, options)
  return response.json()
}

/**
 * 429エラーのハンドリング
 */
function handleRateLimitError() {
  const now = Date.now()
  if (now - rateLimitShownAt > RATE_LIMIT_COOLDOWN) {
    rateLimitShownAt = now
    try {
      const toastStore = useToastStore()
      toastStore.showRateLimitError()
    } catch (e) {
      // ストアが利用できない場合はアラート
      alert('429 error!!\n無料のスプレッドシート使ってるからAPIが限界やわ!!')
    }
  }
}

/**
 * グローバルfetchのオーバーライド（自動429ハンドリング）
 */
export function setupGlobalFetchInterceptor() {
  const originalFetch = window.fetch

  window.fetch = async function (...args) {
    const response = await originalFetch.apply(this, args)

    if (response.status === 429) {
      handleRateLimitError()
    }

    return response
  }
}
