from linebot.models import FlexSendMessage
from bot_instance import line_bot_api
from utils.template_loader import load_template
from services.economy import EconomyService


def handle_message(event, text):
    if text in ["ヘルプ", "help", "使い方", "説明書", "manual"]:
        user_id = event.source.user_id

        # 管理者かどうかでテンプレートを切り替え
        if EconomyService.is_admin(user_id):
            manual_flex = load_template("manual_admin_carousel.json")
            alt_text = "管理者用ガイド"
        else:
            manual_flex = load_template("manual_carousel.json")
            alt_text = "使い方ガイド"

        if manual_flex:
            line_bot_api.reply_message(
                event.reply_token,
                FlexSendMessage(alt_text=alt_text, contents=manual_flex),
            )
            return True
    return False
