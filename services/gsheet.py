import os
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from utils.cache import goals_cache, cached


class GSheetService:
    _instance = None
    _client = None
    _doc = None

    @classmethod
    def _connect(cls):
        """スプレッドシートへの接続を確立（内部利用）"""
        if cls._client and cls._doc:
            return

        try:
            creds_json = os.environ.get("GOOGLE_CREDENTIALS")
            sheet_id = os.environ.get("SPREADSHEET_ID")

            if not creds_json or not sheet_id:
                print("【Error】環境変数が不足しています")
                return

            creds_dict = json.loads(creds_json)
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive",
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            cls._client = gspread.authorize(creds)
            cls._doc = cls._client.open_by_key(sheet_id)
        except Exception as e:
            print(f"【Error】GSheet接続失敗: {e}")

    @classmethod
    def get_worksheet(cls, sheet_name):
        """シート名を指定してワークシートを取得"""
        cls._connect()
        if not cls._doc:
            return None
        try:
            return cls._doc.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            print(f"【Error】シート '{sheet_name}' が見つかりません")
            return None

    @classmethod
    def get_spreadsheet(cls):
        """スプレッドシート本体を取得（シート追加用）"""
        cls._connect()
        return cls._doc

    @staticmethod
    def log_activity(user_id, user_name, today, time, subject=""):
        """学習記録ログを study_log シートに保存（動的カラムマッピング）"""
        row_index = GSheetService.log_activity_with_row(
            user_id, user_name, today, time, subject
        )
        return row_index is not None

    @staticmethod
    def log_activity_with_row(user_id, user_name, today, time, subject=""):
        """学習記録ログを保存し、追加した行番号を返す（原子性サポート）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            print("【Error】study_log シートが見つかりません。作成してください。")
            return None

        try:
            # ヘッダー行を取得してカラム位置を特定
            headers = sheet.row_values(1)
            if not headers:
                print("【Error】ヘッダー情報が取得できません")
                return None

            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            # データ用配列初期化
            row_data = [""] * len(headers)

            def set_val(name, val):
                if name in col_map:
                    row_data[col_map[name]] = val

            set_val("user_id", user_id)
            set_val("display_name", user_name)
            set_val("date", today)
            set_val("start_time", time)
            set_val("status", "STARTED")
            set_val("subject", subject)

            sheet.append_row(row_data)
            # 追加した行の番号を返す（最後の行）
            return sheet.row_count
        except Exception as e:
            print(f"ログ記録エラー: {e}")
            return None

    @staticmethod
    def delete_study_log_row(row_index):
        """指定した行を削除（ロールバック用）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            sheet.delete_rows(row_index)
            return True
        except Exception as e:
            print(f"行削除エラー: {e}")
            return False

    @staticmethod
    def cancel_study(user_id, user_name=None):
        """学習記録をキャンセル（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False

        all_records = sheet.get_all_values()
        if not all_records:
            return False

        headers = all_records[0]
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_uid = col_map.get("user_id")
        idx_name = col_map.get("display_name")
        idx_end = col_map.get("end_time")
        idx_status = col_map.get("status")

        if idx_status is None:
            return False

        target_row = None

        # 後ろから検索
        for i in range(len(all_records), 1, -1):
            row = all_records[i - 1]
            if not row:
                continue

            def get_val(idx):
                return (
                    str(row[idx]).strip() if idx is not None and idx < len(row) else ""
                )

            is_match = False
            if idx_uid is not None and get_val(idx_uid) == str(user_id):
                is_match = True
            elif (
                user_name
                and idx_name is not None
                and get_val(idx_name) == str(user_name)
            ):
                is_match = True

            if is_match:
                end_val = get_val(idx_end)
                status_val = get_val(idx_status)

                # 終了時刻が空 かつ statusがSTARTED (念のため)
                if end_val == "" and status_val == "STARTED":
                    target_row = i
                    break

        if target_row:
            try:
                sheet.update_cell(target_row, idx_status + 1, "CANCELLED")
                return True
            except Exception as e:
                print(f"Cancel Study Error: {e}")
                return False
        return False

    @staticmethod
    def get_all_active_sessions():
        """全ユーザーのアクティブセッション（STARTED）を取得"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return []

        all_records = sheet.get_all_values()
        if not all_records:
            return []

        headers = all_records[0]
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_uid = col_map.get("user_id")
        idx_name = col_map.get("display_name")
        idx_status = col_map.get("status")
        idx_start = col_map.get("start_time")
        idx_subj = col_map.get("subject")
        idx_date = col_map.get("date")

        if idx_status is None:
            return []

        active_sessions = []
        seen_users = set()  # 同じユーザーの重複を防ぐ

        # 後ろから検索（最新を優先）
        for i in range(len(all_records) - 1, 0, -1):
            row = all_records[i]
            if not row:
                continue

            def get_val(idx):
                return (
                    str(row[idx]).strip() if idx is not None and idx < len(row) else ""
                )

            status_val = get_val(idx_status)
            if status_val != "STARTED":
                continue

            user_id = get_val(idx_uid) if idx_uid is not None else ""
            if user_id in seen_users:
                continue
            seen_users.add(user_id)

            user_name = get_val(idx_name) if idx_name is not None else ""
            start_time = get_val(idx_start) if idx_start is not None else ""
            subject = get_val(idx_subj) if idx_subj is not None else ""
            date = get_val(idx_date) if idx_date is not None else ""

            active_sessions.append(
                {
                    "user_id": user_id,
                    "user_name": user_name,
                    "start_time": start_time,
                    "subject": subject,
                    "date": date,
                }
            )

        return active_sessions

    @staticmethod
    def get_user_active_session(user_id, user_name=None):
        """ユーザーのアクティブセッション（STARTED）を取得"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return None

        all_records = sheet.get_all_values()
        if not all_records:
            return None

        headers = all_records[0]
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_uid = col_map.get("user_id")
        idx_name = col_map.get("display_name")
        idx_status = col_map.get("status")
        idx_start = col_map.get("start_time")
        idx_subj = col_map.get("subject")

        if idx_status is None:
            return None

        # 後ろから検索
        for i in range(len(all_records), 1, -1):
            row = all_records[i - 1]
            if not row:
                continue

            def get_val(idx):
                return (
                    str(row[idx]).strip() if idx is not None and idx < len(row) else ""
                )

            # Match Logic
            is_match = False
            if idx_uid is not None and get_val(idx_uid) == str(user_id):
                is_match = True
            elif (
                user_name
                and idx_name is not None
                and get_val(idx_name) == str(user_name)
            ):
                is_match = True

            if is_match:
                status_val = get_val(idx_status)
                if status_val == "STARTED":
                    start_time = get_val(idx_start) if idx_start is not None else ""
                    subject = get_val(idx_subj) if idx_subj is not None else ""
                    return {
                        "row_index": i,
                        "start_time": start_time,
                        "subject": subject,
                    }
                return None  # 最新の記録がSTARTEDでなければアクティブなし
        return None

    @staticmethod
    def update_end_time(user_id, end_time, user_name=None):
        """終了時刻を study_log シートに更新（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return None

        all_records = sheet.get_all_values()
        if not all_records:
            return None

        headers = all_records[0]
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_uid = col_map.get("user_id")
        idx_name = col_map.get("display_name")
        idx_end = col_map.get("end_time")
        idx_status = col_map.get("status")
        idx_start = col_map.get("start_time")
        idx_subj = col_map.get("subject")

        if idx_status is None or idx_end is None:
            return None

        target_row = None

        # 後ろから検索
        for i in range(len(all_records), 1, -1):
            row = all_records[i - 1]
            if not row:
                continue

            def get_val(idx):
                return (
                    str(row[idx]).strip() if idx is not None and idx < len(row) else ""
                )

            # Match Logic
            is_match = False
            if idx_uid is not None and get_val(idx_uid) == str(user_id):
                is_match = True
            elif (
                user_name
                and idx_name is not None
                and get_val(idx_name) == str(user_name)
            ):
                is_match = True

            # EndTime, Status
            if is_match:
                end_val = get_val(idx_end)
                status_val = get_val(idx_status)

                if end_val == "" and status_val == "STARTED":
                    target_row = i
                    break

        if target_row:
            sheet.update_cell(target_row, idx_end + 1, end_time)
            sheet.update_cell(target_row, idx_status + 1, "PENDING")

            subject = ""
            if idx_subj is not None and idx_subj < len(all_records[target_row - 1]):
                subject = all_records[target_row - 1][idx_subj]

            start_time = ""
            if idx_start is not None and idx_start < len(all_records[target_row - 1]):
                start_time = all_records[target_row - 1][idx_start]

            return {
                "start_time": start_time,
                "row_index": target_row,
                "subject": subject,
            }
        return None

    @staticmethod
    def update_study_stats(row_index, duration, rank):
        """学習時間とランクを study_log シートに追記（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_dur = col_map.get("duration_min")
            idx_rank = col_map.get("rank_score")

            if idx_dur is not None:
                sheet.update_cell(row_index, idx_dur + 1, duration)
            if idx_rank is not None:
                sheet.update_cell(row_index, idx_rank + 1, rank)
            return True
        except Exception as e:
            print(f"Stats Update Error: {e}")
            return False

    @staticmethod
    def update_study_details(row_index, comment, concentration):
        """学習の成果と集中度を study_log シートに追記（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_com = col_map.get("comment")
            idx_conc = col_map.get("concentration")

            if idx_com is not None:
                sheet.update_cell(row_index, idx_com + 1, comment)
            if idx_conc is not None:
                sheet.update_cell(row_index, idx_conc + 1, concentration)
            return True
        except Exception as e:
            print(f"Details Update Error: {e}")
            return False

    @staticmethod
    def get_pending_studies():
        """承認待ちの学習記録を取得（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return []

        pending = []
        try:
            records = sheet.get_all_values()
            if not records:
                return []

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_status = col_map.get("status")
            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_start = col_map.get("start_time")
            idx_end = col_map.get("end_time")
            idx_subject = col_map.get("subject")
            idx_comment = col_map.get("comment")
            idx_duration = col_map.get("duration_min")

            if idx_status is None:
                return []

            # ヘッダー飛ばす
            for i, row in enumerate(records[1:], start=2):
                if not row:
                    continue

                def get_val(idx):
                    return (
                        str(row[idx]).strip()
                        if idx is not None and idx < len(row)
                        else ""
                    )

                if get_val(idx_status) == "PENDING":
                    pending.append(
                        {
                            "row_index": i,
                            "user_id": get_val(idx_uid),
                            "user_name": get_val(idx_name),
                            "date": get_val(idx_date),
                            "start_time": get_val(idx_start),
                            "end_time": get_val(idx_end),
                            "subject": get_val(idx_subject) or "勉強",
                            "comment": get_val(idx_comment),
                            "duration_min": get_val(idx_duration),
                        }
                    )
        except Exception as e:
            print(f"Pending Study Error: {e}")
        return pending

    @staticmethod
    def get_user_latest_pending_session(user_id, user_name=None):
        """ユーザーの最新のPENDING（コメント待ち）セッションを取得（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return None

        all_records = sheet.get_all_values()
        if not all_records:
            return None

        headers = all_records[0]
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_status = col_map.get("status")
        idx_uid = col_map.get("user_id")
        idx_name = col_map.get("display_name")
        idx_comment = col_map.get("comment")
        idx_dur = col_map.get("duration_min")
        idx_subj = col_map.get("subject")
        idx_start = col_map.get("start_time")

        if idx_status is None:
            return None

        # 後ろから検索
        for i in range(len(all_records), 1, -1):
            row = all_records[i - 1]
            if not row:
                continue

            def get_val(idx):
                return (
                    str(row[idx]).strip() if idx is not None and idx < len(row) else ""
                )

            is_match = False
            if idx_uid is not None and get_val(idx_uid) == str(user_id):
                is_match = True
            elif (
                user_name
                and idx_name is not None
                and get_val(idx_name) == str(user_name)
            ):
                is_match = True

            if is_match and get_val(idx_status) == "PENDING":
                comment = get_val(idx_comment)
                if not comment:
                    dur_str = get_val(idx_dur)

                    return {
                        "row_index": i,
                        "start_time": get_val(idx_start),
                        "minutes": int(dur_str) if dur_str.isdigit() else 0,
                        "subject": get_val(idx_subj),
                        "state": "WAITING_COMMENT",
                    }
        return None

    @staticmethod
    def approve_study(row_index):
        """学習記録を承認済みに更新（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            print(f"approve_study: sheet not found")
            return False
        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            if idx_status is None:
                print(f"approve_study: status column not found in headers: {headers}")
                return False  # Status column not found

            current_status = sheet.cell(row_index, idx_status + 1).value
            if current_status == "APPROVED":
                print(f"approve_study: row {row_index} already approved")
                return False

            sheet.update_cell(row_index, idx_status + 1, "APPROVED")
            return True
        except Exception as e:
            print(f"approve_study error: {e}")
            return False

    @staticmethod
    def reject_study(row_index):
        """学習記録を却下（REJECTED）に更新（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            print(f"reject_study: sheet not found")
            return False
        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            if idx_status is None:
                print(f"reject_study: status column not found in headers: {headers}")
                return False

            current_status = sheet.cell(row_index, idx_status + 1).value
            if current_status == "APPROVED":
                print(f"reject_study: row {row_index} already approved, cannot reject")
                return False

            sheet.update_cell(row_index, idx_status + 1, "REJECTED")
            return True
        except Exception as e:
            print(f"reject_study error: {e}")
            return False

    @staticmethod
    def check_timeout_sessions(timeout_minutes=90):
        """制限時間を超えた学習セッションを強制終了する（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return []

        try:
            all_records = sheet.get_all_values()
            if not all_records:
                return []

            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_status = col_map.get("status")
            idx_end = col_map.get("end_time")
            idx_date = col_map.get("date")
            idx_start = col_map.get("start_time")
            idx_uid = col_map.get("user_id")
            idx_subj = col_map.get("subject")

            # 必須カラムチェック
            if (
                idx_status is None
                or idx_end is None
                or idx_date is None
                or idx_start is None
            ):
                return []

            expired_sessions = []

            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

            for i in range(1, len(all_records)):
                row = all_records[i]

                # 安全なアクセス
                def get_val(idx):
                    return row[idx] if idx is not None and idx < len(row) else ""

                status = get_val(idx_status)
                end_time = get_val(idx_end)

                if status == "STARTED" and end_time == "":
                    date_str = get_val(idx_date)
                    start_time_str = get_val(idx_start)

                    try:
                        start_dt = datetime.datetime.strptime(
                            f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S"
                        )
                        start_dt = start_dt.replace(
                            tzinfo=datetime.timezone(datetime.timedelta(hours=9))
                        )

                        duration = now - start_dt
                        duration_minutes = int(duration.total_seconds() / 60)

                        if duration_minutes >= timeout_minutes:
                            force_end_dt = start_dt + datetime.timedelta(
                                minutes=timeout_minutes
                            )
                            force_end_time_str = force_end_dt.strftime("%H:%M:%S")

                            row_index = i + 1

                            sheet.update_cell(
                                row_index, idx_end + 1, force_end_time_str
                            )
                            sheet.update_cell(row_index, idx_status + 1, "PENDING")

                            uid = get_val(idx_uid)
                            subject = get_val(idx_subj)

                            expired_sessions.append(
                                {
                                    "user_id": uid,
                                    "row_index": row_index,
                                    "minutes": timeout_minutes,
                                    "subject": subject,
                                    "start_time": start_time_str,
                                }
                            )
                    except Exception as e:
                        print(f"Date Parse Error: {e}")
                        continue

            return expired_sessions

        except Exception as e:
            print(f"Check Timeout Error: {e}")
            return []

    # ==================== 目標管理機能 ====================

    @staticmethod
    def get_or_create_goals_sheet():
        """goalsシートを取得、なければ作成"""
        try:
            sheet = GSheetService.get_worksheet("goals")
            if sheet:
                return sheet

            # シートが存在しない場合は作成
            doc = GSheetService.get_spreadsheet()
            if not doc:
                return None

            sheet = doc.add_worksheet(title="goals", rows=100, cols=10)
            # ヘッダー行を追加
            headers = [
                "id",
                "user_id",
                "user_name",
                "title",
                "description",
                "target_date",
                "created_at",
                "status",
                "completed_at",
            ]
            sheet.append_row(headers)
            print("【Info】goalsシートを作成しました")
            return sheet
        except Exception as e:
            print(f"【Error】goalsシート取得/作成エラー: {e}")
            return None

    @staticmethod
    def add_goal(user_id, user_name, title, description, target_date):
        """目標を追加"""
        sheet = GSheetService.get_or_create_goals_sheet()
        if not sheet:
            return False, "シートが見つかりません"

        try:
            # 新しいIDを生成（行数ベース）
            all_records = sheet.get_all_values()
            new_id = len(all_records)  # ヘッダー含むのでそのまま

            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            created_at = now.strftime("%Y-%m-%d %H:%M:%S")

            row_data = [
                new_id,
                user_id,
                user_name,
                title,
                description,
                target_date,
                created_at,
                "ACTIVE",
                "",
            ]
            sheet.append_row(row_data)
            return True, new_id
        except Exception as e:
            print(f"【Error】目標追加エラー: {e}")
            return False, str(e)

    @staticmethod
    @cached(goals_cache)
    def get_all_goals():
        """全ユーザーの目標を取得（ACTIVEのみ）"""
        sheet = GSheetService.get_or_create_goals_sheet()
        if not sheet:
            return []

        try:
            all_records = sheet.get_all_values()
            if len(all_records) <= 1:
                return []

            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            goals = []
            for row in all_records[1:]:
                if len(row) < len(headers):
                    row.extend([""] * (len(headers) - len(row)))

                status = row[col_map.get("status", 7)] if "status" in col_map else ""
                if status != "ACTIVE":
                    continue

                goals.append(
                    {
                        "id": row[col_map.get("id", 0)],
                        "user_id": row[col_map.get("user_id", 1)],
                        "user_name": row[col_map.get("user_name", 2)],
                        "title": row[col_map.get("title", 3)],
                        "description": row[col_map.get("description", 4)],
                        "target_date": row[col_map.get("target_date", 5)],
                        "created_at": row[col_map.get("created_at", 6)],
                        "status": status,
                    }
                )

            # target_dateで昇順ソート（近い日付が先）
            goals.sort(key=lambda x: x.get("target_date", "9999-99-99"))
            return goals
        except Exception as e:
            print(f"【Error】目標取得エラー: {e}")
            return []

    @staticmethod
    def get_user_goals(user_id):
        """特定ユーザーの目標を取得"""
        all_goals = GSheetService.get_all_goals()
        return [g for g in all_goals if g.get("user_id") == user_id]

    @staticmethod
    def complete_goal(goal_id, user_id):
        """目標を完了にする"""
        sheet = GSheetService.get_or_create_goals_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_id = col_map.get("id", 0)
            idx_uid = col_map.get("user_id", 1)
            idx_status = col_map.get("status", 7)
            idx_completed = col_map.get("completed_at", 8)

            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_id and str(row[idx_id]) == str(goal_id):
                    # ユーザーIDも確認
                    if len(row) > idx_uid and row[idx_uid] == user_id:
                        now = datetime.datetime.now(
                            datetime.timezone(datetime.timedelta(hours=9))
                        )
                        sheet.update_cell(i, idx_status + 1, "COMPLETED")
                        sheet.update_cell(
                            i, idx_completed + 1, now.strftime("%Y-%m-%d %H:%M:%S")
                        )
                        return True
            return False
        except Exception as e:
            print(f"【Error】目標完了エラー: {e}")
            return False

    @staticmethod
    def delete_goal(goal_id, user_id):
        """目標を削除する（ステータスをDELETEDに変更）"""
        sheet = GSheetService.get_or_create_goals_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_id = col_map.get("id", 0)
            idx_uid = col_map.get("user_id", 1)
            idx_status = col_map.get("status", 7)

            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_id and str(row[idx_id]) == str(goal_id):
                    if len(row) > idx_uid and row[idx_uid] == user_id:
                        sheet.update_cell(i, idx_status + 1, "DELETED")
                        return True
            return False
        except Exception as e:
            print(f"【Error】目標削除エラー: {e}")
            return False

    @staticmethod
    def update_goal(goal_id, user_id, title, description, target_date):
        """目標を更新する"""
        sheet = GSheetService.get_or_create_goals_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_id = col_map.get("id", 0)
            idx_uid = col_map.get("user_id", 1)
            idx_title = col_map.get("title", 3)
            idx_desc = col_map.get("description", 4)
            idx_target = col_map.get("target_date", 5)

            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_id and str(row[idx_id]) == str(goal_id):
                    if len(row) > idx_uid and row[idx_uid] == user_id:
                        sheet.update_cell(i, idx_title + 1, title)
                        sheet.update_cell(i, idx_desc + 1, description)
                        sheet.update_cell(i, idx_target + 1, target_date)
                        return True
            return False
        except Exception as e:
            print(f"【Error】目標更新エラー: {e}")
            return False

    # ============== 本棚機能 ==============

    @staticmethod
    def get_or_create_bookshelf_sheet():
        """bookshelfシートを取得または作成"""
        sheet = GSheetService.get_worksheet("bookshelf")
        if sheet:
            return sheet

        # シートが存在しない場合は作成
        try:
            spreadsheet = GSheetService.get_spreadsheet()
            if not spreadsheet:
                return None

            sheet = spreadsheet.add_worksheet(title="bookshelf", rows=1000, cols=15)
            headers = [
                "book_id",
                "user_id",
                "title",
                "author",
                "subject",
                "cover_url",
                "total_pages",
                "current_page",
                "progress",
                "created_at",
                "status",
            ]
            sheet.append_row(headers)
            print("【Info】bookshelfシートを作成しました")
            return sheet
        except Exception as e:
            print(f"【Error】bookshelfシート作成エラー: {e}")
            return None

    @staticmethod
    def get_bookshelf(user_id):
        """ユーザーの本棚を取得"""
        sheet = GSheetService.get_or_create_bookshelf_sheet()
        if not sheet:
            return []

        try:
            all_records = sheet.get_all_values()
            if len(all_records) <= 1:
                return []

            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id", 1)
            idx_status = col_map.get("status", 10)

            books = []
            for row in all_records[1:]:
                if len(row) > idx_uid and row[idx_uid] == str(user_id):
                    # DELETEDは除外
                    status = row[idx_status] if len(row) > idx_status else ""
                    if status == "DELETED":
                        continue

                    book = {
                        h: (row[i] if i < len(row) else "") for h, i in col_map.items()
                    }
                    # 進捗計算
                    total = int(book.get("total_pages") or 0)
                    current = int(book.get("current_page") or 0)
                    book["progress"] = int((current / total) * 100) if total > 0 else 0
                    books.append(book)
            return books
        except Exception as e:
            print(f"【Error】本棚取得エラー: {e}")
            return []

    @staticmethod
    def add_book(
        user_id, title, author="", subject="その他", cover_url="", total_pages=None
    ):
        """本を本棚に追加"""
        sheet = GSheetService.get_or_create_bookshelf_sheet()
        if not sheet:
            return False, "シートが見つかりません"

        try:
            import uuid

            book_id = str(uuid.uuid4())[:8]
            now = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=9))
            ).strftime("%Y-%m-%d %H:%M:%S")

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            row_data = [""] * len(headers)

            def set_val(name, val):
                if name in col_map:
                    row_data[col_map[name]] = val

            set_val("book_id", book_id)
            set_val("user_id", user_id)
            set_val("title", title)
            set_val("author", author)
            set_val("subject", subject)
            set_val("cover_url", cover_url)
            set_val("total_pages", total_pages if total_pages else "")
            set_val("current_page", "0")
            set_val("progress", "0")
            set_val("created_at", now)
            set_val("status", "ACTIVE")

            sheet.append_row(row_data)
            return True, book_id
        except Exception as e:
            print(f"【Error】本追加エラー: {e}")
            return False, str(e)

    @staticmethod
    def update_book_progress(book_id, user_id, current_page):
        """本の進捗を更新"""
        sheet = GSheetService.get_or_create_bookshelf_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_id = col_map.get("book_id", 0)
            idx_uid = col_map.get("user_id", 1)
            idx_total = col_map.get("total_pages", 6)
            idx_current = col_map.get("current_page", 7)
            idx_progress = col_map.get("progress", 8)

            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_id and row[idx_id] == str(book_id):
                    if len(row) > idx_uid and row[idx_uid] == str(user_id):
                        total = (
                            int(row[idx_total])
                            if len(row) > idx_total and row[idx_total]
                            else 0
                        )
                        progress = (
                            int((int(current_page) / total) * 100) if total > 0 else 0
                        )

                        sheet.update_cell(i, idx_current + 1, str(current_page))
                        sheet.update_cell(i, idx_progress + 1, str(progress))
                        return True
            return False
        except Exception as e:
            print(f"【Error】本の進捗更新エラー: {e}")
            return False

    @staticmethod
    def delete_book(book_id, user_id):
        """本を本棚から削除（ステータスをDELETEDに変更）"""
        sheet = GSheetService.get_or_create_bookshelf_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_id = col_map.get("book_id", 0)
            idx_uid = col_map.get("user_id", 1)
            idx_status = col_map.get("status", 10)

            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_id and row[idx_id] == str(book_id):
                    if len(row) > idx_uid and row[idx_uid] == str(user_id):
                        sheet.update_cell(i, idx_status + 1, "DELETED")
                        return True
            return False
        except Exception as e:
            print(f"【Error】本の削除エラー: {e}")
            return False

    # ============== 通知機能 ==============

    @staticmethod
    def get_or_create_notifications_sheet():
        """notificationsシートを取得または作成"""
        sheet = GSheetService.get_worksheet("notifications")
        if sheet:
            return sheet

        try:
            spreadsheet = GSheetService.get_spreadsheet()
            if not spreadsheet:
                return None

            sheet = spreadsheet.add_worksheet(title="notifications", rows=1000, cols=10)
            headers = [
                "id",
                "user_id",
                "type",
                "title",
                "message",
                "icon",
                "read",
                "created_at",
            ]
            sheet.append_row(headers)
            print("【Info】notificationsシートを作成しました")
            return sheet
        except Exception as e:
            print(f"【Error】notificationsシート作成エラー: {e}")
            return None

    @staticmethod
    def add_notification(user_id, type_str, title, message, icon="📢"):
        """ユーザーに通知を追加"""
        sheet = GSheetService.get_or_create_notifications_sheet()
        if not sheet:
            return False

        try:
            import uuid

            notif_id = str(uuid.uuid4())[:8]
            now = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=9))
            ).strftime("%Y-%m-%d %H:%M:%S")

            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            row_data = [""] * len(headers)

            def set_val(name, val):
                if name in col_map:
                    row_data[col_map[name]] = val

            set_val("id", notif_id)
            set_val("user_id", user_id)
            set_val("type", type_str)
            set_val("title", title)
            set_val("message", message)
            set_val("icon", icon)
            set_val("read", "false")
            set_val("created_at", now)

            sheet.append_row(row_data)
            return True
        except Exception as e:
            print(f"【Error】通知追加エラー: {e}")
            return False

    @staticmethod
    def get_user_notifications(user_id, unread_only=True):
        """ユーザーの通知を取得"""
        sheet = GSheetService.get_or_create_notifications_sheet()
        if not sheet:
            return []

        try:
            all_records = sheet.get_all_values()
            if len(all_records) <= 1:
                return []

            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id", 1)
            idx_read = col_map.get("read", 6)

            notifications = []
            for row in all_records[1:]:
                if len(row) > idx_uid and row[idx_uid] == str(user_id):
                    is_read = (
                        row[idx_read].lower() == "true"
                        if len(row) > idx_read
                        else False
                    )
                    if unread_only and is_read:
                        continue

                    notif = {
                        h: (row[i] if i < len(row) else "") for h, i in col_map.items()
                    }
                    notifications.append(notif)

            # 最新順にソート
            notifications.reverse()
            return notifications[:20]  # 最大20件
        except Exception as e:
            print(f"【Error】通知取得エラー: {e}")
            return []

    @staticmethod
    def mark_notification_read(notif_id, user_id):
        """通知を既読にする"""
        sheet = GSheetService.get_or_create_notifications_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_id = col_map.get("id", 0)
            idx_uid = col_map.get("user_id", 1)
            idx_read = col_map.get("read", 6)

            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_id and row[idx_id] == str(notif_id):
                    if len(row) > idx_uid and row[idx_uid] == str(user_id):
                        sheet.update_cell(i, idx_read + 1, "true")
                        return True
            return False
        except Exception as e:
            print(f"【Error】通知既読更新エラー: {e}")
            return False

    @staticmethod
    def mark_all_notifications_read(user_id):
        """ユーザーの全通知を既読にする"""
        sheet = GSheetService.get_or_create_notifications_sheet()
        if not sheet:
            return False

        try:
            all_records = sheet.get_all_values()
            headers = all_records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id", 1)
            idx_read = col_map.get("read", 6)

            updates = []
            for i, row in enumerate(all_records[1:], start=2):
                if len(row) > idx_uid and row[idx_uid] == str(user_id):
                    if len(row) > idx_read and row[idx_read].lower() != "true":
                        updates.append((i, idx_read + 1, "true"))

            # バッチ更新
            for row_idx, col_idx, val in updates:
                sheet.update_cell(row_idx, col_idx, val)
            return True
        except Exception as e:
            print(f"【Error】全通知既読更新エラー: {e}")
            return False
