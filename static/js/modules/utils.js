// Sound Management
const sounds = {
  poweron: new Audio('/static/assets/sounds/Power-on.mp3'),
  click: new Audio('/static/assets/sounds/mouse_click.mp3'),
  select1: new Audio('/static/assets/sounds/select1.mp3'),
  select3: new Audio('/static/assets/sounds/select3.mp3'),
  levelup: new Audio('/static/assets/sounds/Correct5.mp3')
};

export const playSound = (name) => {
  try {
    sounds[name].currentTime = 0;
    sounds[name].play().catch(e => console.log('Sound blocked'));
  } catch (e) { }
};

export const formatNumber = (num) => {
  if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k';
  return Math.floor(num);
};