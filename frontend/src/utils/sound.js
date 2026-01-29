// 音声ファイルの管理クラス
class SoundManager {
  constructor() {
    this.sounds = {
      click: null,
      buy: null,
      levelup: null,
      milestone: null,
      prestige: null
    }
    this.enabled = true
    this.initialized = false
  }

  // 初期化（ユーザーインタラクション後に呼ぶ必要がある）
  init() {
    if (this.initialized) return

    // ここで音声ファイルを読み込む
    // assets/sounds/ ディレクトリにファイルを配置してください
    // mp3ファイルのパスを指定します
    try {
      this.sounds.click = new Audio('/static/sounds/click.mp3')
      this.sounds.buy = new Audio('/static/sounds/buy.mp3') 
      this.sounds.levelup = new Audio('/static/sounds/levelup.mp3')
      this.sounds.milestone = new Audio('/static/sounds/milestone.mp3')
      this.sounds.prestige = new Audio('/static/sounds/prestige.mp3')

      // プリロード設定
      Object.values(this.sounds).forEach(audio => {
        if (audio) {
          audio.load()
          audio.volume = 0.5
        }
      })
      
      this.initialized = true
    } catch (e) {
      console.warn('Sound initialization failed:', e)
    }
  }

  play(name) {
    if (!this.enabled || !this.initialized || !this.sounds[name]) return

    try {
      // 再生位置をリセットして連続再生可能にする
      const sound = this.sounds[name]
      sound.currentTime = 0
      sound.play().catch(e => {
        // 自動再生ポリシーなどでブロックされた場合は無視
        console.debug('Sound play blocked:', e)
      })
    } catch (e) {
      console.error('Error playing sound:', e)
    }
  }

  toggle() {
    this.enabled = !this.enabled
    return this.enabled
  }
}

export const soundManager = new SoundManager()
