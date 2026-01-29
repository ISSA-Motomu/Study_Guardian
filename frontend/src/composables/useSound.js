import { ref } from 'vue'

const sounds = {
  poweron: '/static/sounds/poweron.mp3',
  click: '/static/sounds/click.mp3',
  select1: '/static/sounds/select1.mp3',
  select2: '/static/sounds/select2.mp3',
  select3: '/static/sounds/select3.mp3',
  levelup: '/static/sounds/levelup.mp3',
  attack: '/static/sounds/attack.mp3',
  defeat: '/static/sounds/defeat.mp3',
  coin: '/static/sounds/coin.mp3'
}

const audioCache = {}
const isMuted = ref(false)

export function useSound() {
  const playSound = (name) => {
    if (isMuted.value) return
    const path = sounds[name]
    if (!path) {
      console.warn(`Sound '${name}' not found`)
      return
    }

    try {
      if (!audioCache[name]) {
        audioCache[name] = new Audio(path)
      }
      const audio = audioCache[name]
      audio.currentTime = 0
      audio.play().catch(() => { })
    } catch (e) {
      console.error('Sound error:', e)
    }
  }

  const toggleMute = () => {
    isMuted.value = !isMuted.value
    return isMuted.value
  }

  return {
    playSound,
    toggleMute,
    isMuted
  }
}
