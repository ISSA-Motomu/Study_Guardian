import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class GSheetService:
    _instance = None
    _sheet = None

    @classmethod
    def get_sheet(cls):
        """スプレッドシートへの接続を確立（シングルトンパターン）"""
        if cls._sheet:
            return cls._sheet

        try:
            creds_json = os.environ.get("GOOGLE_CREDENTIALS")
            sheet_id = os.environ.get("SPREADSHEET_ID")
            
            if not creds_json or not sheet_id:
                print("【Error】環境変数が不足しています")
                return None

            creds_dict = json.loads(creds_json)
            scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            client = gspread.authorize(creds)
            
            # シート取得（今は1枚目固定だが、後でシート名指定に変えられるように設計）
            cls._sheet = client.open_by_key(sheet_id).sheet1
            return cls._sheet
        except Exception as e:
            print(f"【Error】GSheet接続失敗: {e}")
            return None

    @staticmethod
    def log_activity(user_id, user_name, today, time, activity_type="START"):
        """ログを記録する汎用メソッド"""
        sheet = GSheetService.get_sheet()
        if not sheet: return False
        
        # 将来的に activity_type で列を変えたりできる
        # 現在は単純な追記のみ実装
        sheet.append_row([user_id, user_name, today, time, ""])
        return True

    @staticmethod
    def update_end_time(user_id, end_time):
        """終了時刻を更新する"""
        sheet = GSheetService.get_sheet()
        if not sheet: return None

        all_records = sheet.get_all_values()
        target_row = None
        
        # 後ろから検索
        for i in range(len(all_records), 0, -1):
            row = all_records[i-1]
            # ID一致 かつ 終了時刻(E列=index4)が空
            if len(row) >= 5 and row[0] == user_id and row[4] == "":
                target_row = i
                break
        
        if target_row:
            sheet.update_cell(target_row, 5, end_time)
            return {
                "start_time": all_records[target_row-1][3],
                "row_index": target_row
            }
        return None