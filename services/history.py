import datetime
from services.gsheet import GSheetService
from services.economy import EconomyService


class HistoryService:
    @staticmethod
    def get_all_transactions():
        """全取引履歴を取得（Web表示用）"""
        sheet = GSheetService.get_worksheet("transactions")
        if not sheet:
            return []

        try:
            records = sheet.get_all_records()
            # 新しい順にソート
            sorted_records = sorted(
                records, key=lambda x: x.get("timestamp", ""), reverse=True
            )
            return sorted_records
        except Exception as e:
            print(f"All History Error: {e}")
            return []

    @staticmethod
    def get_admin_history(limit=10):
        """管理用：最近の取引履歴を取得"""
        sheet = GSheetService.get_worksheet("transactions")
        if not sheet:
            return []

        try:
            records = sheet.get_all_records()
            # 新しい順にソート
            sorted_records = sorted(
                records, key=lambda x: x.get("timestamp", ""), reverse=True
            )
            return sorted_records[:limit]
        except Exception as e:
            print(f"Admin History Error: {e}")
            return []

    @staticmethod
    def get_user_study_stats(user_id):
        """ユーザーの学習履歴統計（週間・月間）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return {"weekly": 0, "monthly": 0, "total": 0}

        now = datetime.datetime.now()
        week_start = now - datetime.timedelta(days=7)
        month_start = now - datetime.timedelta(days=30)

        stats = {"weekly": 0, "monthly": 0, "total": 0}

        try:
            records = sheet.get_all_values()
            # Header skip
            for row in records[1:]:
                # row: [id, name, date, start, end, status]
                if len(row) < 6:
                    continue
                if row[0] != user_id:
                    continue
                if row[5] != "APPROVED":
                    continue  # 承認済みのみ

                date_str = row[2]
                start_str = row[3]
                end_str = row[4]

                try:
                    log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

                    # 時間計算
                    s = datetime.datetime.strptime(start_str, "%H:%M:%S")
                    e = datetime.datetime.strptime(end_str, "%H:%M:%S")
                    if e < s:
                        e += datetime.timedelta(days=1)
                    minutes = int((e - s).total_seconds() / 60)

                    stats["total"] += minutes

                    if log_date >= week_start:
                        stats["weekly"] += minutes

                    if log_date >= month_start:
                        stats["monthly"] += minutes

                except:
                    continue

        except Exception as e:
            print(f"Study Stats Error: {e}")

        return stats

    @staticmethod
    def get_user_job_history(user_id, limit=5):
        """ユーザーの完了したジョブ履歴"""
        sheet = GSheetService.get_worksheet("jobs")
        if not sheet:
            return []

        jobs = []
        try:
            records = sheet.get_all_records()
            user_jobs = [
                r
                for r in records
                if str(r.get("worker_id")) == user_id and r.get("status") == "CLOSED"
            ]
            # ID(timestamp)で降順ソートと仮定
            # job_id = job_1234567890
            sorted_jobs = sorted(
                user_jobs, key=lambda x: x.get("job_id", ""), reverse=True
            )
            return sorted_jobs[:limit]
        except Exception as e:
            print(f"Job History Error: {e}")
            return []

    @staticmethod
    def get_leaderboard():
        """全ユーザーのランキング（EXP順）"""
        users = EconomyService.get_all_users()
        # current_expでソート
        try:
            ranked = sorted(
                users, key=lambda x: int(x.get("current_exp", 0)), reverse=True
            )
            return ranked
        except:
            return users
