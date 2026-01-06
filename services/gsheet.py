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

    @staticmethod
    def log_activity(user_id, user_name, today, time, subject=""):
        """学習記録ログを study_log シートに保存"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            print("【Error】study_log シートが見つかりません。作成してください。")
            return False

        try:
            # A:ID, B:名前, C:日付, D:開始, E:終了, F:ステータス, G:Duration, H:Rank, I:Subject
            sheet.append_row(
                [user_id, user_name, today, time, "", "STARTED", "", "", subject]
            )
            return True
        except Exception as e:
            print(f"ログ記録エラー: {e}")
            return False

    @staticmethod
    def cancel_study(user_id):
        """学習記録をキャンセル（削除またはステータス変更）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False

        all_records = sheet.get_all_values()
        target_row = None

        # 後ろから検索して、まだ終了していない(STARTED)記録を探す
        for i in range(len(all_records), 0, -1):
            row = all_records[i - 1]
            # ID一致 かつ 終了時刻(E列=index4)が空
            if len(row) >= 5 and row[0] == user_id and row[4] == "":
                target_row = i
                break

        if target_row:
            try:
                # 行ごと削除するのが一番きれいだが、行番号がずれるリスクがあるため
                # ステータスを "CANCELLED" に変更する
                sheet.update_cell(target_row, 6, "CANCELLED")
                return True
            except Exception as e:
                print(f"Cancel Study Error: {e}")
                return False
        return False

    @staticmethod
    def update_end_time(user_id, end_time):
        """終了時刻を study_log シートに更新"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return None

        all_records = sheet.get_all_values()
        target_row = None

        # 後ろから検索
        for i in range(len(all_records), 0, -1):
            row = all_records[i - 1]
            # ID一致 かつ 終了時刻(E列=index4)が空
            if len(row) >= 5 and row[0] == user_id and row[4] == "":
                target_row = i
                break

        if target_row:
            # E列(5):終了時刻, F列(6):ステータス
            sheet.update_cell(target_row, 5, end_time)
            sheet.update_cell(target_row, 6, "PENDING")

            # 教科(I列=index8)を取得
            subject = ""
            if len(all_records[target_row - 1]) >= 9:
                subject = all_records[target_row - 1][8]

            return {
                "start_time": all_records[target_row - 1][3],
                "row_index": target_row,
                "subject": subject,
            }
        return None

    @staticmethod
    def update_study_stats(row_index, duration, rank):
        """学習時間とランクを study_log シートに追記"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            # G列(7): Duration, H列(8): Rank
            sheet.update_cell(row_index, 7, duration)
            sheet.update_cell(row_index, 8, rank)
            return True
        except Exception as e:
            print(f"Stats Update Error: {e}")
            return False

    @staticmethod
    def update_study_details(row_index, comment, concentration):
        """学習の成果と集中度を study_log シートに追記"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            # J列(10): Comment, K列(11): Concentration
            sheet.update_cell(row_index, 10, comment)
            sheet.update_cell(row_index, 11, concentration)
            return True
        except Exception as e:
            print(f"Details Update Error: {e}")
            return False

    @staticmethod
    def get_pending_studies():
        """承認待ちの学習記録を取得"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return []

        pending = []
        try:
            records = sheet.get_all_values()
            # ヘッダー飛ばす
            for i, row in enumerate(records[1:], start=2):
                # F列(index 5)が "PENDING"
                if len(row) >= 6 and row[5] == "PENDING":
                    pending.append(
                        {
                            "row_index": i,
                            "user_id": row[0],
                            "user_name": row[1],
                            "date": row[2],
                            "start_time": row[3],
                            "end_time": row[4],
                        }
                    )
        except Exception as e:
            print(f"Pending Study Error: {e}")
        return pending

    @staticmethod
    def get_user_latest_pending_session(user_id):
        """ユーザーの最新のPENDING（コメント待ち）セッションを取得"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return None

        all_records = sheet.get_all_values()

        # 後ろから検索
        for i in range(len(all_records), 0, -1):
            row = all_records[i - 1]
            # ID一致 かつ Status(F列=5)が"PENDING"
            if len(row) >= 6 and row[0] == user_id and row[5] == "PENDING":
                # コメント(J列=9)がまだ空であることを確認
                comment = row[9] if len(row) >= 10 else ""
                if not comment:
                    return {
                        "row_index": i,
                        "start_time": row[3],
                        "minutes": int(row[6])
                        if len(row) >= 7 and row[6].isdigit()
                        else 0,
                        "subject": row[8] if len(row) >= 9 else "",
                        "state": "WAITING_COMMENT",
                    }
        return None

    @staticmethod
    def approve_study(row_index):
        """学習記録を承認済みに更新"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            # 既に承認済みかチェック (F列=6)
            current_status = sheet.cell(row_index, 6).value
            if current_status == "APPROVED":
                return False

            sheet.update_cell(row_index, 6, "APPROVED")
            return True
        except:
            return False

    @staticmethod
    def reject_study(row_index):
        """学習記録を却下（REJECTED）に更新"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False
        try:
            # 既に承認済みかチェック (F列=6)
            current_status = sheet.cell(row_index, 6).value
            if current_status == "APPROVED":
                return False

            sheet.update_cell(row_index, 6, "REJECTED")
            return True
        except:
            return False

    @staticmethod
    def check_timeout_sessions(timeout_minutes=90):
        """制限時間を超えた学習セッションを強制終了する"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return []

        try:
            all_records = sheet.get_all_values()
            expired_sessions = []

            # 現在時刻 (JST)
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))

            # ヘッダーを除く
            for i in range(1, len(all_records)):
                row = all_records[i]
                # A:ID, B:Name, C:Date, D:Start, E:End, F:Status
                if len(row) < 6:
                    continue

                status = row[5]
                end_time = row[4]

                if status == "STARTED" and end_time == "":
                    # 開始日時を構築
                    date_str = row[2]  # YYYY-MM-DD
                    start_time_str = row[3]  # HH:MM:SS

                    try:
                        start_dt = datetime.datetime.strptime(
                            f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M:%S"
                        )
                        # JST timezone info might be missing in strptime result, assume it is JST because 'now' is JST
                        start_dt = start_dt.replace(
                            tzinfo=datetime.timezone(datetime.timedelta(hours=9))
                        )

                        duration = now - start_dt
                        duration_minutes = int(duration.total_seconds() / 60)

                        if duration_minutes >= timeout_minutes:
                            # 強制終了時刻 (開始 + 90分)
                            force_end_dt = start_dt + datetime.timedelta(
                                minutes=timeout_minutes
                            )
                            force_end_time_str = force_end_dt.strftime("%H:%M:%S")

                            # シート更新 (行番号は i + 1)
                            row_index = i + 1
                            sheet.update_cell(row_index, 5, force_end_time_str)
                            sheet.update_cell(row_index, 6, "PENDING")

                            expired_sessions.append(
                                {
                                    "user_id": row[0],
                                    "row_index": row_index,
                                    "minutes": timeout_minutes,
                                    "subject": row[8] if len(row) > 8 else "",
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
