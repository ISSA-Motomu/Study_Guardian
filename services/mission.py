import datetime
from services.gsheet import GSheetService
from services.economy import EconomyService


class MissionService:
    @staticmethod
    def create_mission(target_user_id, title, description, reward, client_id):
        """ミッションを作成（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False, "missionsシートが見つかりません"

        try:
            mission_id = f"msn_{int(datetime.datetime.now().timestamp())}"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            row_data = [""] * len(headers)

            def set_val(key, val):
                idx = col_map.get(key)
                if idx is not None:
                    row_data[idx] = val

            set_val("mission_id", mission_id)
            set_val("user_id", target_user_id)
            set_val("title", title)
            set_val("description", description)
            set_val("reward", reward)
            set_val("status", "OPEN")
            set_val("created_at", now_str)
            set_val("completed_at", "")

            sheet.append_row(row_data)
            return True, mission_id
        except Exception as e:
            print(f"Create Mission Error: {e}")
            return False, str(e)

    @staticmethod
    def get_active_missions(user_id):
        """ユーザーの進行中ミッションを取得（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return []

        missions = []
        try:
            rows = sheet.get_all_values()
            if len(rows) > 1:
                headers = rows[0]
                col_map = {str(h).strip(): i for i, h in enumerate(headers)}

                idx_mid = col_map.get("mission_id")
                idx_uid = col_map.get("user_id")
                idx_status = col_map.get("status")

                if idx_mid is None or idx_uid is None or idx_status is None:
                    return []

                idx_title = col_map.get("title")
                idx_desc = col_map.get("description")
                idx_reward = col_map.get("reward")
                idx_created = col_map.get("created_at")

                def get_val(r, idx):
                    return r[idx] if idx is not None and idx < len(r) else ""

                for r in rows[1:]:
                    if (
                        get_val(r, idx_uid) == str(user_id)
                        and get_val(r, idx_status) == "OPEN"
                    ):
                        missions.append(
                            {
                                "mission_id": get_val(r, idx_mid),
                                "title": get_val(r, idx_title),
                                "description": get_val(r, idx_desc),
                                "reward": get_val(r, idx_reward),
                                "status": get_val(r, idx_status),
                                "created_at": get_val(r, idx_created),
                            }
                        )
        except Exception as e:
            print(f"Get Missions Error: {e}")
        return missions

    @staticmethod
    def complete_mission(mission_id, user_id):
        """ミッションを完了報告（PENDING_APPROVALにする）（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False

        try:
            cell = sheet.find(str(mission_id))
            if not cell:
                return False

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_status = col_map.get("status")
            if idx_uid is None:
                return False

            # 本人確認
            target_uid = sheet.cell(cell.row, idx_uid + 1).value
            if str(target_uid) != str(user_id):
                return False

            # Status update to PENDING
            if idx_status is not None:
                sheet.update_cell(cell.row, idx_status + 1, "PENDING")
            return True
        except Exception as e:
            print(f"Complete Mission Error: {e}")
            return False

    @staticmethod
    def approve_mission(mission_id):
        """ミッション承認（報酬付与＆バッジ付与）（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False, "Sheet not found"

        try:
            cell = sheet.find(str(mission_id))
            if not cell:
                return False, "Mission not found"

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_title = col_map.get("title")
            idx_reward = col_map.get("reward")
            idx_status = col_map.get("status")
            idx_completed = col_map.get("completed_at")

            if idx_status is None or idx_uid is None:
                return False, "Columns missing"

            row = cell.row
            # Get details
            user_id = sheet.cell(row, idx_uid + 1).value
            title = (
                sheet.cell(row, idx_title + 1).value if idx_title is not None else ""
            )
            reward_val = (
                sheet.cell(row, idx_reward + 1).value if idx_reward is not None else "0"
            )
            if not str(reward_val).isdigit():
                reward_val = 0
            reward = int(reward_val)

            status = sheet.cell(row, idx_status + 1).value

            if status != "PENDING":
                return False, "Not pending"

            # Update Status
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.update_cell(row, idx_status + 1, "COMPLETED")
            if idx_completed is not None:
                sheet.update_cell(row, idx_completed + 1, now_str)

            # Give Reward
            EconomyService.add_exp(user_id, reward, f"MISSION_{mission_id}")

            # Give Badge
            badge_key = f"mission_{mission_id}"
            EconomyService.add_inventory_item(user_id, badge_key, 1)

            return True, {"user_id": user_id, "title": title, "reward": reward}

        except Exception as e:
            print(f"Approve Mission Error: {e}")
            return False, str(e)

    @staticmethod
    def get_pending_reviews():
        """承認待ちのミッションを取得（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("missions")
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

                idx_mid = col_map.get("mission_id")
                idx_uid = col_map.get("user_id")
                idx_title = col_map.get("title")
                idx_desc = col_map.get("description")
                idx_reward = col_map.get("reward")
                idx_created = col_map.get("created_at")

                def get_val(r, idx):
                    return r[idx] if idx is not None and idx < len(r) else ""

                for r in rows[1:]:
                    if get_val(r, idx_status) == "PENDING":
                        pending.append(
                            {
                                "mission_id": get_val(r, idx_mid),
                                "user_id": get_val(r, idx_uid),
                                "title": get_val(r, idx_title),
                                "description": get_val(r, idx_desc),
                                "reward": get_val(r, idx_reward),
                                "status": get_val(r, idx_status),
                                "created_at": get_val(r, idx_created),
                            }
                        )
        except Exception as e:
            print(f"Get Pending Missions Error: {e}")
        return pending

    @staticmethod
    def reject_mission(mission_id):
        """ミッション却下（OPENに戻す）（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False

        try:
            cell = sheet.find(str(mission_id))
            if not cell:
                return False

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            if idx_status is None:
                return False

            # Status update to OPEN
            sheet.update_cell(cell.row, idx_status + 1, "OPEN")
            return True
        except Exception as e:
            print(f"Reject Mission Error: {e}")
            return False
