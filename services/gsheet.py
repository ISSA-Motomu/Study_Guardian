import os
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials


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
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            print("【Error】study_log シートが見つかりません。作成してください。")
            return False

        try:
            # ヘッダー行を取得してカラム位置を特定
            headers = sheet.row_values(1)
            if not headers:
                print("【Error】ヘッダー情報が取得できません")
                return False

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
            return True
        except Exception as e:
            print(f"ログ記録エラー: {e}")
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
            return False
        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            if idx_status is None:
                return False  # Status column not found

            current_status = sheet.cell(row_index, idx_status + 1).value
            if current_status == "APPROVED":
                return False

            sheet.update_cell(row_index, idx_status + 1, "APPROVED")
            return True
        except:
            return False

    @staticmethod
    def reject_study(row_index):
        """学習記録を却下（REJECTED）に更新（動的カラムマッピング）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}
            idx_status = col_map.get("status")
            if idx_status is None:
                return False

            current_status = sheet.cell(row_index, idx_status + 1).value
            if current_status == "APPROVED":
                return False

            sheet.update_cell(row_index, idx_status + 1, "REJECTED")
            return True
        except:
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
