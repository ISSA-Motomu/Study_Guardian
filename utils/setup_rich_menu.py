import os
import sys
from linebot import LineBotApi
from linebot.models import (
    RichMenu,
    RichMenuSize,
    RichMenuArea,
    RichMenuBounds,
    MessageAction,
)
from dotenv import load_dotenv

# プロジェクトルートのパスを追加してbot_instanceをインポートできるようにする
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

load_dotenv()

LINE_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
if not LINE_ACCESS_TOKEN:
    print("Error: LINE_CHANNEL_ACCESS_TOKEN is not set in .env")
    sys.exit(1)

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)


def create_rich_menu(image_path):
    # 1. リッチメニューの定義を作成
    # 2500x1686 (Large) の6分割レイアウトを想定
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=True,
        name="Main Menu",
        chat_bar_text="メニューを開く",
        areas=[
            # 上段左: 勉強開始
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                action=MessageAction(label="勉強開始", text="勉強開始"),
            ),
            # 上段中: 勉強終了
            RichMenuArea(
                bounds=RichMenuBounds(x=833, y=0, width=834, height=843),
                action=MessageAction(label="勉強終了", text="勉強終了"),
            ),
            # 上段右: 状況 (Status)
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=0, width=833, height=843),
                action=MessageAction(label="状況", text="状況"),
            ),
            # 下段左: ジョブ
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=843, width=833, height=843),
                action=MessageAction(label="ジョブ", text="ジョブ"),
            ),
            # 下段中: ショップ
            RichMenuArea(
                bounds=RichMenuBounds(x=833, y=843, width=834, height=843),
                action=MessageAction(label="ショップ", text="ショップ"),
            ),
            # 下段右: 管理
            RichMenuArea(
                bounds=RichMenuBounds(x=1667, y=843, width=833, height=843),
                action=MessageAction(label="管理", text="管理"),
            ),
        ],
    )

    # 2. リッチメニューを作成 (ID取得)
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
    print(f"Rich Menu Created: {rich_menu_id}")

    # 3. 画像をアップロード
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    with open(image_path, "rb") as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/jpeg", f)
    print("Image Uploaded.")

    # 4. デフォルトのリッチメニューとして設定
    line_bot_api.set_default_rich_menu(rich_menu_id)
    print("Set as Default Rich Menu.")


if __name__ == "__main__":
    # 画像パスを指定してください (例: menu.jpg)
    # 画像サイズは 2500x1686 推奨
    IMAGE_PATH = "menu.jpg"

    if len(sys.argv) > 1:
        IMAGE_PATH = sys.argv[1]

    create_rich_menu(IMAGE_PATH)
