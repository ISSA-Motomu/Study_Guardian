import { playSound, formatNumber } from './utils.js';

export const gameModule = {
  data() {
    return {
      // RPG Game State
      gameState: {
        stage: 1,
        areaName: '始まりの大地',
        currentHp: 100,
        maxHp: 100,
        enemyName: 'スライム',
        enemyIcon: '💧',
        isBoss: false,
        dps: 0,
        clickDamage: 1,
        lastTick: Date.now()
      },
      dmgEffects: [], // { id, x, y, val, isCrit }
      isHit: false, // animation trigger
      battleInterval: null,
      dmgIdCounter: 0,

      // Shop Data
      shopItems: [],
      selectedItem: null,
      showBuyModal: false,
      buyComment: '',
    }
  },
  methods: {
    formatNumber, // Make avail in template
    // --- RPG Logic ---
    startBattleLoop() {
      if (this.battleInterval) clearInterval(this.battleInterval);
      this.battleInterval = setInterval(() => {
        if (this.view === 'game') {
          // Auto Attack (DPS)
          if (this.gameState.dps > 0) {
            this.dealDamage(this.gameState.dps / 10); // 10 ticks per second
          }
        }
      }, 100);
    },
    handleManualClick(e) {
      // Click effect coordinates
      const rect = e.target.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      this.dealDamage(this.gameState.clickDamage, true, x, y);
      playSound('click');
    },
    dealDamage(amount, isCrit = false, x = 0, y = 0) {
      this.gameState.currentHp -= amount;
      this.isHit = true;
      setTimeout(() => this.isHit = false, 100);

      // Visual Effect
      if (isCrit || Math.random() < 0.3) {
        const id = this.dmgIdCounter++;
        // Random pos if not specified
        const finalX = x || (window.innerWidth / 2) + (Math.random() * 100 - 50);
        const finalY = y || (window.innerHeight / 2 - 100);

        this.dmgEffects.push({ id, val: amount, x: finalX, y: finalY, isCrit });
        setTimeout(() => {
          this.dmgEffects = this.dmgEffects.filter(d => d.id !== id);
        }, 800);
      }

      if (this.gameState.currentHp <= 0) {
        this.enemyDefeated();
      }
    },
    enemyDefeated() {
      playSound('levelup');
      this.gameState.stage++;

      // Calculate Next Enemy
      // HP = Base * (1.1 ^ Stage)
      const growthRate = 1.1;
      const baseHp = 100;
      const nextHp = Math.floor(baseHp * Math.pow(growthRate, this.gameState.stage));

      this.gameState.maxHp = nextHp;
      this.gameState.currentHp = nextHp;

      // Boss Logic (Every 10 stages)
      this.gameState.isBoss = (this.gameState.stage % 10 === 0);

      // Update Name/Icon
      const enemies = [
        { name: 'スライム', icon: '💧' }, { name: 'コウモリ', icon: '🦇' },
        { name: 'ゴブリン', icon: '👺' }, { name: 'オオカミ', icon: '🐺' },
        { name: 'スケルトン', icon: '💀' }, { name: 'オーク', icon: '👹' },
        { name: 'ゴーレム', icon: '🗿' }, { name: 'ドラゴン', icon: '🐲' }
      ];
      // Cycle through enemies based on stage
      const enemyType = enemies[(this.gameState.stage - 1) % enemies.length];
      this.gameState.enemyName = this.gameState.isBoss ? '??? (BOSS)' : enemyType.name;
      this.gameState.enemyIcon = this.gameState.isBoss ? '👿' : enemyType.icon;

      // Reset Boss HP Multiplier
      if (this.gameState.isBoss) {
        this.gameState.maxHp *= 5; // Boss has 5x HP
        this.gameState.currentHp = this.gameState.maxHp;
      }
    },
    applyStudyDamage(minutes) {
      if (!minutes || minutes <= 0) return;

      this.view = 'game'; // Switch to game view to show effect

      // Calculate Damage
      const stageScaling = Math.pow(1.1, this.gameState.stage);
      const damage = Math.floor(minutes * 100 * stageScaling);

      // Animate generic big hit
      setTimeout(() => {
        this.dealDamage(damage, true); // critical hit visual
        alert(`勉強の成果！\n敵に ${this.formatNumber(damage)} のダメージを与えました！`);
      }, 500);
    },

    // --- Shop Logic ---
    async openShop() {
      playSound('click');
      this.loading = true;
      try {
        const res = await fetch('/api/shop/items');
        const json = await res.json();
        if (json.status === 'ok') {
          this.shopItems = json.data;
          this.view = 'game';
        } else {
          alert("ショップ情報の取得に失敗しました");
        }
      } catch (e) {
        console.error(e);
        alert("通信エラー");
      } finally {
        this.loading = false;
      }
    },
    openBuyModal(item) {
      this.selectedItem = item;
      this.buyComment = '';
      this.showBuyModal = true;
    },
    async confirmBuy() {
      if (!this.selectedItem) return;

      if ((this.user.xp || 0) < this.selectedItem.cost) {
        alert("XPが足りません！");
        return;
      }

      playSound('select3');
      try {
        const res = await fetch('/api/shop/buy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: this.currentUserId,
            item_key: this.selectedItem.key,
            comment: this.buyComment
          })
        });
        const json = await res.json();
        if (json.status === 'ok') {
          alert("購入リクエストを送りました！\n親の承認をお待ちください。");
          this.showBuyModal = false;
          // ポイント表示更新のため再取得
          await this.fetchUserData(this.currentUserId);
        } else {
          alert("購入エラー: " + json.message);
        }
      } catch (e) { alert("通信エラー"); }
    },
  }
};