import datetime
import traceback
from linebot.models import TextSendMessage, FlexSendMessage
from bot_instance import line_bot_api
from services.economy import EconomyService
from services.approval import ApprovalService
from services.shop import ShopService
from services.job import JobService
from utils.template_loader import load_template


def handle_message(event, text):
    try:
        user_id = event.source.user_id

        if text.startswith("タスク追加"):
            if not EconomyService.is_admin(user_id):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="権限がありません。")
                )
                return True

            # Parse args: タスク追加 [Title] [Reward]
            parts = text.split()
            if len(parts) < 3:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="使用法: タスク追加 [タイトル] [報酬]"),
                )
                return True

            # 最後の要素を報酬、それ以外をタイトルとする（タイトルにスペースが含まれる場合に対応）
            try:
                reward = int(parts[-1])
                title = " ".join(parts[1:-1])
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="報酬は数値で指定してください。"),
                )
                return True

            success, result = JobService.create_job(title, reward, "", user_id)
            if success:
                msg = f"タスク「{title}」を作成しました。(報酬: {reward})"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))

                # Notify Users
                all_users = EconomyService.get_all_users()
                target_ids = [
                    str(u["user_id"]) for u in all_users if str(u["user_id"]) != user_id
                ]

                if target_ids:
                    try:
                        line_bot_api.multicast(
                            target_ids,
                            TextSendMessage(
                                text=f"🆕 新しいお手伝いが追加されました！\n\n「{title}」\n報酬: {reward} EXP\n\n早い者勝ちだよ！"
                            ),
                        )
                    except Exception as e:
                        print(f"Multicast Error: {e}")
            else:
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text=f"作成失敗: {result}")
                )
            return True

        if text == "商品追加":
            # Google Form for Item Addition
            form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfFxXNFm-xuB4LMbn8Y6ePX4y46Rl0C34ouTzi7qYYuSSOXWg/viewform"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"商品追加はこちらのフォームから行ってください：\n{form_url}"
                ),
            )
            return True

        if text in ["管理", "承認", "admin"]:
            if not EconomyService.is_admin(user_id):
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="権限がありません。")
                )
                return True

            pending_items = ApprovalService.get_all_pending()

            if not pending_items:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="現在、承認待ちの項目はありません。"),
                )
                return True

            # カルーセル作成
            carousel = load_template("approval_list.json")
            if not carousel:
                print("Error: approval_list.json could not be loaded.")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="テンプレート読み込みエラーが発生しました。"),
                )
                return True

            bubbles = carousel["contents"]

            # ショップアイテムを一度だけ取得（最適化）
            shop_items_cache = None

            for item in pending_items:
                p_type = item["type"]
                data = item["data"]

                # 必須項目のサニタイズ (空文字だとLINE APIエラーになるため)
                user_name = data.get("user_name")
                if not user_name:
                    user_name = str(data.get("user_id", "Unknown"))
                if not user_name:
                    user_name = "Unknown"

                if p_type == "study":
                    bubble = load_template(
                        "approval_card_study.json",
                        user_name=user_name,
                        date=data.get("date", ""),
                        start_time=data.get("start_time", ""),
                        end_time=data.get("end_time", ""),
                        earned_exp=data.get("earned_exp", 0),
                        row_index=data["row_index"],
                        user_id=data["user_id"],
                    )
                    if "earned_exp" not in data:
                        try:
                            s = datetime.datetime.strptime(
                                data["start_time"], "%H:%M:%S"
                            )
                            e = datetime.datetime.strptime(data["end_time"], "%H:%M:%S")
                            if e < s:
                                e += datetime.timedelta(days=1)
                            mins = int((e - s).total_seconds() / 60)
                            if mins > 90:
                                mins = 90
                            bubble = load_template(
                                "approval_card_study.json",
                                user_name=user_name,
                                date=data.get("date", ""),
                                start_time=data.get("start_time", ""),
                                end_time=data.get("end_time", ""),
                                earned_exp=mins,
                                row_index=data["row_index"],
                                user_id=data["user_id"],
                            )
                        except:
                            pass
                    if bubble:
                        bubbles.append(bubble)

                elif p_type == "job":
                    job_title = data.get("job_title")
                    if not job_title:
                        job_title = "無題のタスク"

                    bubble = load_template(
                        "approval_card_job.json",
                        user_name=user_name,
                        job_name=job_title,
                        reward=data["reward"],
                        row_index=data["job_id"],
                        user_id=data["user_id"],
                    )
                    if bubble:
                        bubbles.append(bubble)

                elif p_type == "shop":
                    if shop_items_cache is None:
                        shop_items_cache = ShopService.get_items()

                    item_name = data.get("item_key", "商品")
                    item_info = shop_items_cache.get(data["item_key"])
                    if item_info:
                        item_name = item_info["name"]

                    if not item_name:
                        item_name = "商品"

                    bubble = load_template(
                        "approval_card_shop.json",
                        user_name=user_name,
                        item_name=item_name,
                        cost=data["cost"],
                        row_index=data["request_id"],
                        user_id=data["user_id"],
                    )
                    if bubble:
                        bubbles.append(bubble)

            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text="承認待ち一覧", contents=carousel),
            )
            return True

    except Exception as e:
        print(f"Admin Handler Error: {e}")
        traceback.print_exc()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(
                text="管理機能でエラーが発生しました。ログを確認してください。"
            ),
        )
        return True

    return False
