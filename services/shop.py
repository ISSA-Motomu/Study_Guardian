import datetime
from collections import OrderedDict
from services.gsheet import GSheetService
from utils.cache import shop_items_cache, cached


class ShopService:
    @staticmethod
    def create_request(user_id, item_key, cost, comment="", user_name=""):
        """購入リクエストを作成（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("shop_requests")
        if not sheet:
            return False

        try:
            req_id = f"req_{int(datetime.datetime.now().timestamp())}"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            row_data = [""] * len(headers)

            def set_val(key, val, alt_key=None):
                idx = col_map.get(key)
                if idx is None and alt_key:
                    idx = col_map.get(alt_key)

                if idx is not None:
                    row_data[idx] = val

            set_val("request_id", req_id, "id")
            set_val("user_id", user_id)
            set_val("display_name", user_name, "user_name")
            set_val("item_key", item_key, "item")
            set_val("cost", cost)
            set_val("status", "PENDING")
            set_val("timestamp", now_str, "time")
            set_val("comment", comment)

            sheet.append_row(row_data)
            return req_id
        except Exception as e:
            print(f"Shop Request Error: {e}")
            return False

    @staticmethod
    def get_pending_requests():
        """承認待ちの購入リクエストを取得（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("shop_requests")
        if not sheet:
            return []

        pending = []
        try:
            rows = sheet.get_all_values()
            if len(rows) > 1:
                headers = rows[0]
                col_map = {str(h).strip(): i for i, h in enumerate(headers)}

                idx_status = col_map.get("status")
                if idx_status is None:
                    return []

                def get_val(r, key):
                    idx = col_map.get(key)
                    return r[idx] if idx is not None and idx < len(r) else ""

                for r in rows[1:]:
                    if get_val(r, "status") == "PENDING":
                        # Convert to dict expected by caller
                        row_dict = {k: get_val(r, k) for k in col_map.keys()}
                        # Ensure 'time' exists if timestamp was used
                        if "time" not in row_dict and "timestamp" in row_dict:
                            row_dict["time"] = row_dict["timestamp"]
                        # Ensure request_id exists
                        if not row_dict.get("request_id"):
                            # Try alternative keys
                            row_dict["request_id"] = row_dict.get("id") or row_dict.get("req_id") or ""
                        pending.append(row_dict)
        except Exception as e:
            print(f"Shop Pending Error: {e}")
        return pending

    @staticmethod
    def approve_request(request_id):
        """購入リクエストを承認（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("shop_requests")
        if not sheet:
            return False

        try:
            # request_id は文字列であることを保証する
            cell = sheet.find(str(request_id))
            if not cell:
                return False

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            idx_item = col_map.get("item_key")

            if idx_status is None:
                return False

            # ステータスチェック (PENDING以外なら処理しない)
            current_status = sheet.cell(cell.row, idx_status + 1).value
            if current_status != "PENDING":
                return False

            sheet.update_cell(cell.row, idx_status + 1, "APPROVED")

            # 商品キーを返す（アイテム名取得用）
            item_key = None
            if idx_item is not None:
                item_key = sheet.cell(cell.row, idx_item + 1).value
            return item_key
        except Exception as e:
            print(f"Shop Approve Error: {e}")
            return False

    @staticmethod
    def deny_request(request_id):
        """購入リクエストを却下（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("shop_requests")
        if not sheet:
            return False

        try:
            # request_id は文字列であることを保証する
            cell = sheet.find(str(request_id))
            if not cell:
                return False

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            idx_item = col_map.get("item_key")

            if idx_status is None:
                return False

            # ステータスチェック (PENDING以外なら処理しない)
            current_status = sheet.cell(cell.row, idx_status + 1).value
            if current_status != "PENDING":
                return False

            sheet.update_cell(cell.row, idx_status + 1, "DENIED")

            # 商品キーを返す（アイテム名取得用）
            item_key = None
            if idx_item is not None:
                item_key = sheet.cell(cell.row, idx_item + 1).value
            return item_key
        except Exception as e:
            print(f"Shop Deny Error: {e}")
            return False

    @staticmethod
    @cached(shop_items_cache)
    def get_items():
        """スプレッドシートから商品リストを取得（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("shop_items")
        if not sheet:
            return {}

        try:
            rows = sheet.get_all_values()
            items = OrderedDict()

            if len(rows) > 1:
                headers = rows[0]
                col_map = {str(h).strip(): i for i, h in enumerate(headers)}

                idx_key = col_map.get("item_key")
                idx_name = col_map.get("name")
                idx_cost = col_map.get("cost")
                idx_active = col_map.get("is_active")
                idx_desc = col_map.get("description")

                if idx_key is None or idx_name is None:
                    return {}

                def get_val(r, idx):
                    return r[idx] if idx is not None and idx < len(r) else ""

                for r in rows[1:]:
                    is_active = "TRUE"  # Default if missing
                    if idx_active is not None:
                        is_active = str(get_val(r, idx_active)).strip().upper()

                    if is_active == "TRUE":
                        key = get_val(r, idx_key)
                        name = get_val(r, idx_name)

                        # 名前が空の場合はスキップ (LINE Flex Messageでエラーになるため)
                        if not name:
                            continue

                        cost = 999999
                        cost_str = get_val(r, idx_cost) if idx_cost is not None else ""
                        try:
                            if cost_str:
                                cost = int(cost_str)
                        except:
                            pass

                        desc = get_val(r, idx_desc) if idx_desc is not None else ""

                        items[key] = {
                            "name": name,
                            "cost": cost,
                            "description": desc,
                        }
            return items
        except Exception as e:
            print(f"【Error】商品リスト取得エラー: {e}")
            return {}

    @staticmethod
    def add_item(name, cost, description=""):
        """新しい商品をショップに追加（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("shop_items")
        if not sheet:
            return False, "シートエラー"

        try:
            item_key = f"item_{int(datetime.datetime.now().timestamp())}"

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            row_data = [""] * len(headers)

            def set_val(key, val):
                idx = col_map.get(key)
                if idx is not None:
                    row_data[idx] = val

            set_val("item_key", item_key)
            set_val("name", name)
            set_val("cost", cost)
            set_val("description", description)
            set_val("is_active", "TRUE")

            sheet.append_row(row_data)
            return True, item_key
        except Exception as e:
            print(f"Add Item Error: {e}")
            return False, str(e)
