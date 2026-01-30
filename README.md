
# Study Guardian

学習習慣を楽しく身につけるためのLINE Bot & LIFFアプリケーションです。
勉強時間を記録し、RPGのようにレベルアップやコイン獲得ができるゲーミフィケーション要素を取り入れています。

## 🌟 主な機能

### 📖 学習タイマー
- 科目を選択して勉強時間を計測（ストップウォッチ形式）
- 勉強終了時にメモを残せる機能
- 目標管理機能（進捗バーで可視化）
- 本棚機能（教材を管理・整理）

### ⚔️ ゲーミフィケーション
- 勉強時間に応じてEXP（経験値）を獲得
- レベルアップ機能とランクシステム
- オートバトルシステム（放置RPG）
- 進化ゲーム（ペット育成）
- ガチャシステム

### 📊 データ可視化
- 週間学習グラフ
- ランキング機能
- アクティビティタイムライン
- 学習統計ダッシュボード

### 🛒 ショップ & 報酬
- EXPでご褒美アイテムを購入
- 承認ワークフロー（管理者が承認）
- お手伝いタスク（ジョブ）で報酬獲得

### 🔔 通知システム
- 承認/却下の通知
- アプリ内通知ベル
- LINE通知連携

## 📱 画面構成

| タブ | 機能 |
| --- | --- |
| 📖 勉強 | タイマー、目標、ショップ、本棚 |
| ⚔️ ゲーム | バトル、進化ゲーム、ガチャ |
| 📊 データ | グラフ、ランキング、タイムライン |
| ⚙️ その他 | 設定、統計、実績、管理者メニュー |

## 🛠️ 技術スタック

- **Frontend**: Vue 3 + Pinia + Tailwind CSS + Vite
- **Backend**: Python 3.11 + Flask
- **Platform**: LINE LIFF + Messaging API
- **Database**: Google Sheets (gspread)
- **Hosting**: Render

## 📂 ディレクトリ構造

```text
Study_Guardian/
├── app.py                # Flask アプリケーションエントリーポイント
├── bot_instance.py       # LINE Bot API初期化
├── blueprints/           # Flask Blueprints
│   ├── web.py            # Web API エンドポイント
│   └── bot.py            # LINE Bot Webhook
├── handlers/             # LINEイベントハンドラ
│   ├── study.py          # 勉強関連
│   ├── job.py            # ジョブ関連
│   ├── shop.py           # ショップ関連
│   ├── gacha.py          # ガチャ関連
│   ├── status.py         # ステータス・ランキング
│   ├── admin.py          # 管理者コマンド
│   └── ...
├── services/             # ビジネスロジック
│   ├── gsheet.py         # Google Sheets連携
│   ├── approval.py       # 承認ワークフロー
│   ├── history.py        # 履歴・統計取得
│   ├── economy.py        # 経済システム
│   └── stats.py          # 統計計算
├── frontend/             # Vue 3 フロントエンド
│   ├── src/
│   │   ├── components/   # Vueコンポーネント
│   │   ├── stores/       # Pinia ストア
│   │   ├── composables/  # Vue Composables
│   │   └── ...
│   └── ...
├── templates/            # LINE Flex Message JSON
├── static/               # 静的ファイル
│   └── dist/             # ビルド済みフロントエンド
├── utils/                # ユーティリティ
│   ├── cache.py          # キャッシュ機能
│   └── achievements.py   # 実績システム
└── docs/                 # ドキュメント
```

## ⚙️ 環境変数 (.env)

| 変数名 | 説明 |
| --- | --- |
| `LINE_CHANNEL_ACCESS_TOKEN` | LINE Messaging API トークン |
| `LINE_CHANNEL_SECRET` | LINE Messaging API シークレット |
| `LIFF_ID` | LIFF アプリID |
| `SPREADSHEET_ID` | Google Sheets スプレッドシートID |
| `GOOGLE_CREDENTIALS` | Google Service Account JSON |
| `APP_URL` | アプリの公開URL |

## 🚀 セットアップ

```bash
# 依存関係インストール
pip install -r requirements.txt

# フロントエンドビルド
cd frontend
npm install
npm run build

# 開発サーバー起動
python app.py
```

## 📖 ドキュメント

- [コマンド一覧](./docs/command.md)
- [要件定義](./docs/Requirement.md)
- [ロードマップ](./docs/Roadmap.md)

## 📝 License

© 2025-2026 I (画像配信等に使用)


