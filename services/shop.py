from services.gsheet import GSheetService


class ShopService:
    @staticmethod
    def get_items():
        """スプレッドシートから商品リストを取得"""
        sheet = GSheetService.get_worksheet("shop_items")
        if not sheet:
            return {}

        try:
            records = sheet.get_all_records()
            items = {}
            for row in records:
                # is_activeがTRUEのものだけ抽出
                if str(row.get("is_active")).upper() == "TRUE":
                    key = row.get("item_key")
                    items[key] = {
                        "name": row.get("name"),
                        "cost": int(row.get("cost")),
                        "description": row.get("description", ""),
                    }
            return items
        except Exception as e:
            print(f"【Error】商品リスト取得エラー: {e}")
            return {}
