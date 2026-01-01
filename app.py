import os
import json
import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# .env読み込み（ローカル用）
load_dotenv()

app = Flask(__name__)

# LINE API設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    print("【Error】LINEの環境変数が設定されていません")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google Sheets設定
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GOOGLE_CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS")


def get_worksheet():
    """スプレッドシートに接続してシートを取得する関数"""
    try:
        if not GOOGLE_CREDENTIALS_JSON or not SPREADSHEET_ID:
            print("【Error】Google Sheetsの環境変数が不足しています")
            return None

        # JSON文字列を辞書に変換
        creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)

        # シートを開く（1枚目のシートを取得）
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        return sheet
    except Exception as e:
        print(f"【Error】スプレッドシート接続エラー: {e}")
        return None


@app.route("/")
def hello_world():
    return "Study Guardian is Active!"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_msg = event.message.text
    user_id = event.source.user_id
    # ユーザー名を取得（プロフィール情報）
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name

    # 現在時刻
    now = datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=9))
    )  # 日本時間
    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    sheet = get_worksheet()
    reply_text = ""

    if user_msg == "勉強開始":
        if sheet:
            # A列:User_ID, B:名前, C:日付, D:開始, E:終了
            sheet.append_row([user_id, user_name, today, current_time, ""])
            reply_text = (
                f"【記録開始】\n{current_time} スタート！\n今日も頑張ってえらい！"
            )
        else:
            reply_text = "エラー：記録シートが見つかりません。"

    elif user_msg == "勉強終了":
        if sheet:
            # そのユーザーの今日の最後の「開始」のみの行を探す（簡易実装）
            # 本格的にはもっと検索ロジックが必要ですが、まずはシンプルに「直近の行」を更新します
            all_records = sheet.get_all_values()
            target_row = None

            # 後ろから検索して、自分のIDで、かつ終了時刻(E列)が空の行を探す
            for i in range(len(all_records), 0, -1):
                row = all_records[i - 1]
                # row[0]がID, row[4]が終了時刻（インデックスは0始まりなのでE列は4）
                if len(row) >= 5 and row[0] == user_id and row[4] == "":
                    target_row = i
                    break

            if target_row:
                # E列（5列目）に終了時刻を書き込む
                sheet.update_cell(target_row, 5, current_time)

                # 時間計算（簡易的にメッセージで返す）
                start_time_str = all_records[target_row - 1][3]  # D列
                start_dt = datetime.datetime.strptime(start_time_str, "%H:%M:%S")
                end_dt = datetime.datetime.strptime(current_time, "%H:%M:%S")
                duration = end_dt - start_dt
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _ = divmod(remainder, 60)

                reply_text = f"【記録終了】\nお疲れ様でした！\n勉強時間: {hours}時間{minutes}分\nしっかり休みましょう。"
            else:
                reply_text = "「勉強開始」が押されていないみたいです。\nとりあえず記録しておきます！"
        else:
            reply_text = "エラー：記録シートが見つかりません。"

    else:
        # ボタン以外が押されたとき
        reply_text = "下のメニューから「勉強開始」か「勉強終了」を押してね！"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))


if __name__ == "__main__":
    app.run()
