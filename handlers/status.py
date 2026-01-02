from linebot.models import TextSendMessage, FlexSendMessage
from bot_instance import line_bot_api
from services.economy import EconomyService
from services.history import HistoryService
from utils.template_loader import load_template


def handle_message(event, text):
    user_id = event.source.user_id

    if text in ["状況", "ステータス", "status"]:
        # 1. Adminかどうかチェック
        if EconomyService.is_admin(user_id):
            # --- Admin View (Transaction History) ---
            history = HistoryService.get_admin_history(limit=5)  # LINE上は直近5件だけ

            bubble = load_template("status_admin_view.json")
            # body -> contents[2] is the list container
            list_container = bubble["body"]["contents"][2]["contents"]

            if not history:
                list_container.append(
                    {
                        "type": "text",
                        "text": "履歴なし",
                        "size": "sm",
                        "color": "#aaaaaa",
                    }
                )
            else:
                for tx in history:
                    # tx: tx_id, user_id, amount, tx_type, related_id, timestamp
                    amount = int(tx.get("amount", 0))
                    color = "#ff5555" if amount > 0 else "#5555ff"
                    amount_str = f"+{amount}" if amount > 0 else str(amount)

                    # ユーザー名解決 (簡易的)
                    user_info = EconomyService.get_user_info(str(tx.get("user_id")))
                    user_name = (
                        user_info["display_name"]
                        if user_info
                        else str(tx.get("user_id"))[:4]
                    )

                    row = load_template(
                        "status_row_transaction.json",
                        date=str(tx.get("timestamp"))[5:-3],  # MM-DD HH:MM
                        user=user_name,
                        amount=amount_str,
                        color=color,
                    )
                    list_container.append(row)

            # Web Dashboard / Looker Studio へのリンクボタンを追加
            if "footer" not in bubble:
                bubble["footer"] = {"type": "box", "layout": "vertical", "contents": []}

            import os

            # Looker StudioのURLが設定されていればそちらを優先
            # デフォルト値をコードに埋め込んでおくことで、環境変数がなくても動作するようにする
            looker_url = os.environ.get(
                "LOOKER_STUDIO_URL", "https://lookerstudio.google.com/s/uS2xDhhDtAw"
            )
            base_url = os.environ.get("APP_URL", "https://your-app.herokuapp.com")

            if looker_url:
                uri = looker_url
                label = "Looker Studioで分析"
            else:
                uri = f"{base_url}/admin/dashboard"
                label = "詳細な履歴をWebで見る"

            bubble["footer"]["contents"].append(
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {"type": "uri", "label": label, "uri": uri},
                }
            )

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="管理者ダッシュボード", contents=bubble),
            )
            return True

        else:
            # --- User View (Personal + Ranking) ---

            # A. Personal Stats
            user_info = EconomyService.get_user_info(user_id)
            if not user_info:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="ユーザー登録されていません。何か発言して登録してください。"
                    ),
                )
                return True

            study_stats = HistoryService.get_user_study_stats(user_id)

            # --- Gamification Logic ---
            total_minutes = study_stats.get("total", 0)
            level = int(total_minutes / 60) + 1
            next_level_rem = 60 - (total_minutes % 60)

            # Progress Bar (10 blocks)
            progress = int((total_minutes % 60) / 60 * 10)
            progress_bar = "🟩" * progress + "⬜" * (10 - progress)

            # Rank Logic
            if total_minutes >= 3000:
                rank = "S (Master)"
            elif total_minutes >= 1200:
                rank = "A (Elite)"
            elif total_minutes >= 600:
                rank = "B (Pro)"
            else:
                rank = "C (Rookie)"

            import os

            looker_url = os.environ.get(
                "LOOKER_STUDIO_URL", "https://lookerstudio.google.com/s/uS2xDhhDtAw"
            )

            bubble = load_template(
                "status_user_gamified.json",
                user_id_short=user_id[:4],
                user_name=user_info["display_name"],
                level=level,
                progress_bar=progress_bar,
                next_level_rem=next_level_rem,
                rank=rank,
                current_exp=user_info["current_exp"],
                weekly_study=study_stats["weekly"],
                looker_url=looker_url,
            )

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="マイステータス", contents=bubble),
            )
            return True

    return False
