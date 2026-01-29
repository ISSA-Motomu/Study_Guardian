// Web Audio API を使ったサウンド管理クラス
// 外部ファイル不要で軽量なゲームサウンドを生成

class SoundManager {
  constructor() {
    this.audioContext = null
    this.enabled = true
    this.initialized = false
  }

  // 初期化（ユーザーインタラクション後に呼ぶ必要がある）
  init() {
    if (this.initialized) return
    try {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)()
      this.initialized = true
    } catch (e) {
      console.warn('Web Audio API not supported:', e)
    }
  }

  // ビープ音を生成
  beep(frequency = 440, duration = 0.1, type = 'sine', volume = 0.3) {
    if (!this.enabled || !this.audioContext) return
    
    try {
      const oscillator = this.audioContext.createOscillator()
      const gainNode = this.audioContext.createGain()
      
      oscillator.connect(gainNode)
      gainNode.connect(this.audioContext.destination)
      
      oscillator.type = type
      oscillator.frequency.value = frequency
      
      gainNode.gain.setValueAtTime(volume, this.audioContext.currentTime)
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration)
      
      oscillator.start()
      oscillator.stop(this.audioContext.currentTime + duration)
    } catch (e) {
      console.debug('Sound play error:', e)
    }
  }

  play(name) {
    if (!this.enabled) return
    this.init()
    
    switch (name) {
      case 'click':
        // 軽いクリック音
        this.beep(800, 0.05, 'sine', 0.2)
        break
        
      case 'buy':
        // コイン音（上昇音）
        this.beep(523, 0.08, 'sine', 0.25)
        setTimeout(() => this.beep(659, 0.08, 'sine', 0.25), 50)
        setTimeout(() => this.beep(784, 0.1, 'sine', 0.2), 100)
        break
        
      case 'levelup':
        // レベルアップ音（ファンファーレ）
        this.beep(523, 0.1, 'sine', 0.3)
        setTimeout(() => this.beep(659, 0.1, 'sine', 0.3), 100)
        setTimeout(() => this.beep(784, 0.15, 'sine', 0.3), 200)
        setTimeout(() => this.beep(1047, 0.2, 'sine', 0.25), 350)
        break
        
      case 'milestone':
        // マイルストーン達成音（壮大なファンファーレ）
        this.beep(392, 0.15, 'sine', 0.3)
        setTimeout(() => this.beep(523, 0.15, 'sine', 0.3), 150)
        setTimeout(() => this.beep(659, 0.15, 'sine', 0.3), 300)
        setTimeout(() => this.beep(784, 0.2, 'sine', 0.35), 450)
        setTimeout(() => this.beep(1047, 0.3, 'sine', 0.3), 600)
        setTimeout(() => this.beep(1319, 0.4, 'triangle', 0.25), 800)
        break
        
      case 'prestige':
        // 転生音（荘厳なサウンド）
        for (let i = 0; i < 5; i++) {
          setTimeout(() => this.beep(261.63 * Math.pow(2, i / 3), 0.3, 'sine', 0.2), i * 150)
        }
        setTimeout(() => {
          this.beep(523, 0.5, 'triangle', 0.3)
          this.beep(659, 0.5, 'triangle', 0.25)
          this.beep(784, 0.5, 'triangle', 0.2)
        }, 800)
        break
        
      default:
        this.beep(440, 0.05, 'sine', 0.15)
    }
  }

  toggle() {
    this.enabled = !this.enabled
    return this.enabled
  }
}

export const soundManager = new SoundManager()
