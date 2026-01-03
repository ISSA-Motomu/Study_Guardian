from services.gsheet import GSheetService
import datetime
import json


class EconomyService:
    @staticmethod
    def check_balance(user_id, cost):
        """残高が足りているか確認（足りていればTrue）"""
        user = EconomyService.get_user_info(user_id)
        if not user:
            return False

        # current_expが数値であることを確認しつつ比較
        try:
            current = int(user.get("current_exp", 0))
            return current >= cost
        except:
            return False

    @staticmethod
    def is_admin(user_id):
        """管理権限を持っているか確認"""
        user = EconomyService.get_user_info(user_id)
        if not user:
            return False
        return user.get("role") == "ADMIN"

    @staticmethod
    def get_user_info(user_id):
        """ユーザー情報を取得（なければNone）"""
        sheet = GSheetService.get_worksheet("users")
        if not sheet:
            return None

        # 全データを取得して検索（人数が増えたらfindメソッドなどへ最適化推奨）
        records = sheet.get_all_records()  # ヘッダーがある前提
        for user in records:
            if str(user.get("user_id")) == user_id:
                return user
        return None

    @staticmethod
    def get_all_users():
        """全ユーザー情報を取得"""
        sheet = GSheetService.get_worksheet("users")
        if not sheet:
            return []
        return sheet.get_all_records()

    @staticmethod
    def get_admin_users():
        """Admin権限を持つユーザーのリストを取得"""
        users = EconomyService.get_all_users()
        admins = [u for u in users if u.get("role") == "ADMIN"]
        return admins

    @staticmethod
    def register_user(user_id, display_name):
        """新規ユーザー登録（口座開設）"""
        sheet = GSheetService.get_worksheet("users")
        if not sheet:
            return False

        # すでにいるか確認
        if EconomyService.get_user_info(user_id):
            return True  # 登録済み

        # 新規登録 (初期EXP: 0, Role: USER, Inventory: {}, Rank: E)
        # 列順: user_id, display_name, current_exp, total_study_time, role, inventory_json, rank
        sheet.append_row([user_id, display_name, 0, 0, "USER", "{}", "E"])
        return True

    @staticmethod
    def update_user_rank(user_id, rank):
        """ユーザーのランクを更新"""
        sheet = GSheetService.get_worksheet("users")
        if not sheet:
            return False

        try:
            cell = sheet.find(user_id)
            if cell:
                # Rank is column 7
                sheet.update_cell(cell.row, 7, rank)
                return True
            return False
        except Exception as e:
            print(f"Update Rank Error: {e}")
            return False

    @staticmethod
    def reset_user(user_id):
        """ユーザー情報をリセット（削除）"""
        sheet = GSheetService.get_worksheet("users")
        if not sheet:
            return False

        try:
            cell = sheet.find(user_id)
            if cell:
                sheet.delete_rows(cell.row)
                return True
            return False
        except Exception as e:
            print(f"Reset User Error: {e}")
            return False

    @staticmethod
    def get_user_inventory(user_id):
        """ユーザーの所持品リストを取得"""
        user = EconomyService.get_user_info(user_id)
        if not user:
            return []

        inventory_json = user.get("inventory_json", "{}")
        if not inventory_json:
            inventory_json = "{}"

        try:
            inventory_dict = json.loads(inventory_json)
        except:
            inventory_dict = {}

        # 辞書からリスト形式に変換 (表示用)
        # 定義マスタ (本来は別ファイルやDBで管理すべきだが一旦ここに記述)
        item_master = {
            "ticket_1.5x": {"name": "ポイント 1.5倍", "icon": "🎟"},
            "shield_chores": {"name": "絶対防御", "icon": "🛡"},
            "supple_focus": {"name": "集中サプリ", "icon": "💊"},
            "bonus_100": {"name": "臨時ボーナス", "icon": "💸"},
        }

        items = []
        for item_key, count in inventory_dict.items():
            if count > 0:
                master = item_master.get(item_key, {"name": item_key, "icon": "📦"})
                items.append(
                    {
                        "key": item_key,
                        "name": master["name"],
                        "icon": master["icon"],
                        "count": count,
                    }
                )
        return items

    @staticmethod
    def add_inventory_item(user_id, item_key, count=1):
        """インベントリにアイテムを追加"""
        sheet = GSheetService.get_worksheet("users")
        if not sheet:
            return False

        cell = sheet.find(user_id)
        if not cell:
            return False

        row_num = cell.row
        # inventory_json は F列(6列目)
        inv_cell = sheet.cell(row_num, 6)
        inv_json = inv_cell.value

        try:
            inv_dict = json.loads(inv_json) if inv_json else {}
        except:
            inv_dict = {}

        current_count = inv_dict.get(item_key, 0)
        inv_dict[item_key] = current_count + count

        sheet.update_cell(row_num, 6, json.dumps(inv_dict))
        return True

    @staticmethod
    def add_exp(user_id, amount, related_id="STUDY"):
        """EXPを加算（減算ならマイナス）し、履歴に残す"""
        users_sheet = GSheetService.get_worksheet("users")
        tx_sheet = GSheetService.get_worksheet("transactions")

        if not users_sheet or not tx_sheet:
            return False

        # 1. ユーザーを探して残高更新
        cell = users_sheet.find(user_id)
        if not cell:
            return False

        row_num = cell.row
        # display_name は B列(2列目)、current_exp は C列(3列目)
        user_name = users_sheet.cell(row_num, 2).value
        current_exp_cell = users_sheet.cell(row_num, 3)

        try:
            current_val = int(current_exp_cell.value)
        except:
            current_val = 0
        new_exp = current_val + amount

        # 2. 取引履歴(Transaction)を記録 (原子性担保のため先にログ)
        # 列: tx_id, user_id, amount, tx_type, related_id, timestamp, user_name
        tx_id = f"tx_{int(datetime.datetime.now().timestamp())}"
        tx_type = "REWARD" if amount > 0 else "SPEND"
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            tx_sheet.append_row(
                [tx_id, user_id, amount, tx_type, related_id, now_str, user_name]
            )
        except Exception as e:
            print(f"Transaction Log Error: {e}")
            return False

        # 3. 残高更新
        try:
            users_sheet.update_cell(row_num, 3, new_exp)
        except Exception as e:
            print(f"Balance Update Error: {e}")
            # ログは書けたが残高更新に失敗。不整合だがログ優先。
            return False

        return new_exp
