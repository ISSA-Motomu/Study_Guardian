# Study Guardian - Frontend

Vue 3 + Vite + Pinia による放置ゲーム型学習アプリのフロントエンド

## 📁 ディレクトリ構造

```
frontend/
├── index.html              # エントリーHTML (LIFF SDK含む)
├── package.json            # 依存関係
├── vite.config.js          # Vite設定 (プロキシ、ビルド出力)
├── tailwind.config.js      # Tailwind CSS設定
├── postcss.config.js       # PostCSS設定
└── src/
    ├── main.js             # Vueアプリ初期化
    ├── App.vue             # ルートコンポーネント
    ├── styles/
    │   └── main.css        # グローバルスタイル + Tailwind
    ├── stores/             # Pinia ストア (状態管理)
    │   ├── index.js
    │   ├── user.js         # ユーザー情報・認証
    │   ├── study.js        # 勉強セッション管理
    │   ├── game.js         # 放置ゲームロジック
    │   └── shop.js         # ショップ・購入機能
    ├── composables/        # 再利用可能なロジック
    │   ├── index.js
    │   ├── useSound.js     # サウンド管理
    │   ├── useLiff.js      # LINE LIFF連携
    │   └── useApi.js       # API通信ヘルパー
    └── components/         # UIコンポーネント
        ├── index.js
        ├── common/         # 共通コンポーネント
        │   ├── LoadingSpinner.vue
        │   ├── BottomNav.vue
        │   ├── FloatingButton.vue
        │   └── GlassPanel.vue
        ├── study/          # 勉強機能
        │   ├── StudyView.vue
        │   ├── TimerView.vue
        │   ├── SubjectModal.vue
        │   └── MemoConfirmDialog.vue
        ├── game/           # ゲーム機能
        │   ├── GameView.vue
        │   ├── EnemyDisplay.vue
        │   └── DamageEffect.vue
        ├── data/           # データ・グラフ
        │   ├── DataView.vue
        │   ├── WeeklyChart.vue
        │   └── SubjectChart.vue
        ├── shop/           # ショップ機能
        │   └── BuyModal.vue
        └── admin/          # 管理者機能
            └── AdminView.vue
```

## 🚀 開発方法

```bash
# 依存関係インストール
cd frontend
npm install

# 開発サーバー起動 (ホットリロード)
npm run dev

# 本番ビルド (../static/dist/ に出力)
npm run build
```

## 🎮 放置ゲーム拡張ポイント

### 新しい敵タイプを追加
[src/stores/game.js](src/stores/game.js) の `enemies` 配列を拡張:

```javascript
const enemies = [
  { name: 'スライム', icon: '💧', baseHp: 100 },
  { name: '新しい敵', icon: '🆕', baseHp: 200 },
  // ...
]
```

### 新しいスキル/アビリティ
`src/stores/skills.js` を追加し、`game.js` から参照

### イベント/ボーナス
`src/stores/events.js` を追加し、期間限定イベントを管理

### 装備システム
```
src/stores/equipment.js    # 装備データ
src/components/game/
  ├── EquipmentSlot.vue    # 装備スロット
  └── EquipmentModal.vue   # 装備選択
```

## 📝 設計方針

1. **SFC (Single File Component)**: タグバランス問題を防止
2. **Pinia Store**: グローバル状態の一元管理
3. **Composables**: ロジックの再利用
4. **Teleport**: モーダルをbodyに配置してz-index問題を回避
5. **v-if / v-else**: 条件付きレンダリングの明確化

## 🔗 Flask連携

- `/api/*` へのリクエストは Vite プロキシ経由で Flask へ転送
- 本番環境ではビルド成果物を Flask の `/static/dist/` から配信
