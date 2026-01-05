import datetime
from services.gsheet import GSheetService
from services.economy import EconomyService


class MissionService:
    @staticmethod
    def create_mission(target_user_id, title, description, reward, client_id):
        """ミッションを作成"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False, "missionsシートが見つかりません"

        try:
            mission_id = f"msn_{int(datetime.datetime.now().timestamp())}"
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Columns: mission_id, user_id, title, description, reward, status, created_at, completed_at
            sheet.append_row(
                [
                    mission_id,
                    target_user_id,
                    title,
                    description,
                    reward,
                    "OPEN",
                    now_str,
                    "",
                ]
            )
            return True, mission_id
        except Exception as e:
            print(f"Create Mission Error: {e}")
            return False, str(e)

    @staticmethod
    def get_active_missions(user_id):
        """ユーザーの進行中ミッションを取得"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return []

        missions = []
        try:
            rows = sheet.get_all_values()
            if len(rows) > 1:
                for r in rows[1:]:
                    # r: [id, uid, title, desc, reward, status, created, completed]
                    if len(r) < 6:
                        continue

                    if str(r[1]) == str(user_id) and r[5] == "OPEN":
                        missions.append(
                            {
                                "mission_id": r[0],
                                "title": r[2],
                                "description": r[3],
                                "reward": r[4],
                                "status": r[5],
                                "created_at": r[6],
                            }
                        )
        except Exception as e:
            print(f"Get Missions Error: {e}")
        return missions

    @staticmethod
    def complete_mission(mission_id, user_id):
        """ミッションを完了報告（PENDING_APPROVALにする）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False

        try:
            cell = sheet.find(str(mission_id))
            if not cell:
                return False

            # 本人確認 (B列=2)
            target_uid = sheet.cell(cell.row, 2).value
            if str(target_uid) != str(user_id):
                return False

            # Status update to PENDING
            sheet.update_cell(cell.row, 6, "PENDING")
            return True
        except Exception as e:
            print(f"Complete Mission Error: {e}")
            return False

    @staticmethod
    def approve_mission(mission_id):
        """ミッション承認（報酬付与＆バッジ付与）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False, "Sheet not found"

        try:
            cell = sheet.find(str(mission_id))
            if not cell:
                return False, "Mission not found"

            row = cell.row
            # Get details
            user_id = sheet.cell(row, 2).value
            title = sheet.cell(row, 3).value
            reward = int(sheet.cell(row, 5).value)
            status = sheet.cell(row, 6).value

            if status != "PENDING":
                return False, "Not pending"

            # Update Status
            now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sheet.update_cell(row, 6, "COMPLETED")
            sheet.update_cell(row, 8, now_str)

            # Give Reward
            EconomyService.add_exp(user_id, reward, f"MISSION_{mission_id}")

            # Give Badge (Inventory Item)
            # バッジキーはユニークにするか、汎用バッジにするか。
            # ここでは「ミッション達成バッジ」として、inventoryには
            # {"mission_msn_12345": 1} のように保存し、表示側でタイトルを解決する仕組みが必要だが
            # 現状のバッジシステムはキーと画像が紐づいている。
            # 簡易的に「汎用ミッションバッジ」を付与し、そのメタデータを持たせるのは難しい（inventoryはただのCount）。
            # なので、EconomyServiceに「実績履歴」を持たせるか、
            # あるいは「バッジ」としてカウントするだけにするか。
            # ユーザーの要望は「ステータスAchievementに順次バッジが付与されていく」。
            # つまり、アイコンが並ぶイメージ。
            # ここでは inventory に "mission_{mission_id}" を追加し、
            # StatusServiceでそれを解釈して表示するようにする。

            badge_key = f"mission_{mission_id}"
            EconomyService.add_inventory_item(user_id, badge_key, 1)

            return True, {"user_id": user_id, "title": title, "reward": reward}

        except Exception as e:
            print(f"Approve Mission Error: {e}")
            return False, str(e)

    @staticmethod
    def get_pending_reviews():
        """承認待ちのミッションを取得"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return []

        pending = []
        try:
            rows = sheet.get_all_values()
            if len(rows) > 1:
                for r in rows[1:]:
                    # r: [id, uid, title, desc, reward, status, created, completed]
                    if len(r) < 6:
                        continue

                    if r[5] == "PENDING":
                        pending.append(
                            {
                                "mission_id": r[0],
                                "user_id": r[1],
                                "title": r[2],
                                "description": r[3],
                                "reward": r[4],
                                "status": r[5],
                                "created_at": r[6],
                            }
                        )
        except Exception as e:
            print(f"Get Pending Missions Error: {e}")
        return pending

    @staticmethod
    def reject_mission(mission_id):
        """ミッション却下（OPENに戻す）"""
        sheet = GSheetService.get_worksheet("missions")
        if not sheet:
            return False

        try:
            cell = sheet.find(str(mission_id))
            if not cell:
                return False

            # Status update to OPEN
            sheet.update_cell(cell.row, 6, "OPEN")
            return True
        except Exception as e:
            print(f"Reject Mission Error: {e}")
            return False
