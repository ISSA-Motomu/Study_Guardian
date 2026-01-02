import urllib.parse
import json


class StatusService:
    @staticmethod
    def create_life_skills_gui(user_data, inventory_items):
        # 1. パラメータ計算
        # user_data keys: user_id, display_name, current_exp, total_study_time, role, inventory_json

        total_study_time = int(user_data.get("total_study_time", 0))
        current_exp = int(user_data.get("current_exp", 0))

        # 仮のロジック
        stats = {
            "知力": min(100, int(total_study_time / 10)),  # 1000分でMAX
            "労働": min(100, int(current_exp / 50)),  # 仮: EXPを労働の代替指標に
            "資産": min(100, int(current_exp / 100)),  # EXPが資産
            "規律": 80,  # 仮
            "運": 50,  # 仮
        }

        # 2. レーダーチャート画像のURL生成 (QuickChart API)
        chart_config = {
            "type": "radar",
            "data": {
                "labels": ["Brain", "Labor", "Cash", "Rule", "Luck"],
                "datasets": [
                    {
                        "label": "User Stats",
                        "data": [
                            stats["知力"],
                            stats["労働"],
                            stats["資産"],
                            stats["規律"],
                            stats["運"],
                        ],
                        "backgroundColor": "rgba(39, 172, 178, 0.5)",
                        "borderColor": "#27ACB2",
                        "pointBackgroundColor": "#fff",
                    }
                ],
            },
            "options": {
                "scale": {"ticks": {"min": 0, "max": 100, "display": False}},
                "legend": {"display": False},
            },
        }

        chart_url = "https://quickchart.io/chart?c=" + urllib.parse.quote(
            json.dumps(chart_config)
        )

        # 3. インベントリ（所持品）のカルーセル作成
        inventory_bubbles = []

        if not inventory_items:
            inventory_bubbles.append(
                {
                    "type": "text",
                    "text": "所持品はありません",
                    "color": "#aaaaaa",
                    "size": "xs",
                    "align": "center",
                }
            )
        else:
            for item in inventory_items:
                # item structure: {"name": "...", "icon": "...", "count": 1}
                inventory_bubbles.append(
                    {
                        "type": "box",
                        "layout": "vertical",
                        "backgroundColor": "#f0f0f0",
                        "cornerRadius": "md",
                        "paddingAll": "md",
                        "width": "80px",
                        "contents": [
                            {
                                "type": "text",
                                "text": item.get("icon", "📦"),
                                "size": "xxl",
                                "align": "center",
                            },
                            {
                                "type": "text",
                                "text": item.get("name", "Item"),
                                "size": "xxs",
                                "align": "center",
                                "wrap": True,
                                "margin": "sm",
                            },
                            {
                                "type": "text",
                                "text": f"x{item.get('count', 1)}",
                                "size": "xs",
                                "align": "center",
                                "color": "#27ACB2",
                                "weight": "bold",
                            },
                        ],
                    }
                )

        # 4. Flex Message 全体構築
        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "LIFE SKILLS",
                        "weight": "bold",
                        "color": "#27ACB2",
                        "size": "sm",
                    },
                    {
                        "type": "text",
                        "text": f"{user_data.get('display_name')} の生活力",
                        "weight": "bold",
                        "size": "xl",
                    },
                ],
            },
            "hero": {
                "type": "image",
                "url": chart_url,
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "separator", "margin": "md"},
                    {
                        "type": "text",
                        "text": "🎒 ITEMS",
                        "weight": "bold",
                        "size": "sm",
                        "margin": "md",
                        "color": "#555555",
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": inventory_bubbles,
                        "spacing": "sm",
                        "margin": "sm",
                    },
                ],
            },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "message",
                            "label": "🎲 ガチャ",
                            "text": "ガチャ",
                        },
                        "style": "primary",
                        "color": "#ff5555",
                    }
                ],
            },
        }
        return bubble
