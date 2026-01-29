import { ref } from 'vue'

const sounds = {
  poweron: '/static/assets/sounds/Power-on.mp3',
  click: '/static/assets/sounds/mouse_click.mp3',
  select1: '/static/assets/sounds/select1.mp3',
  select2: '/static/assets/sounds/select2.mp3',
  select3: '/static/assets/sounds/select3.mp3',
  levelup: '/static/assets/sounds/Correct5.mp3',
  attack: '/static/assets/sounds/select6.mp3',
  defeat: '/static/assets/sounds/error2.mp3',
  coin: '/static/assets/sounds/confirm1.mp3'
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
