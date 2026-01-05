from services.gsheet import GSheetService
from services.job import JobService
from services.shop import ShopService
from services.economy import EconomyService


class ApprovalService:
    @staticmethod
    def get_all_pending():
        """全ての承認待ち項目をフラットなリストで取得"""
        results = []

        # ユーザー名解決用のマッピング作成
        users = EconomyService.get_all_users()
        user_map = {str(u.get("user_id")): u.get("display_name") for u in users}

        # 1. 勉強記録
        studies = GSheetService.get_pending_studies()
        for s in studies:
            # s keys: row_index, user_id, user_name, date, start_time, end_time
            # 勉強記録は既にuser_nameが入っている場合が多いが、念のため補完も可能
            # ここでは既存ロジックを維持しつつ、必要ならmapから取ることも検討できるが
            # GSheetService側で既に名前が入っているはずなのでそのままにする
            results.append({"type": "study", "data": s})

        # 2. ジョブ完了報告
        jobs = JobService.get_pending_reviews()
        for j in jobs:
            worker_id = str(j.get("worker_id"))
            worker_name = user_map.get(worker_id, worker_id)

            # j keys: job_id, title, reward, status, client_id, worker_id, deadline
            data = {
                "job_id": j.get("job_id"),
                "user_id": worker_id,
                "user_name": worker_name,
                "job_title": j.get("title"),
                "reward": j.get("reward"),
                "time": j.get("finished_at", ""),
            }
            results.append({"type": "job", "data": data})

        # 3. ショップ購入リクエスト
        shops = ShopService.get_pending_requests()
        for s in shops:
            uid = str(s.get("user_id"))
            uname = user_map.get(uid, uid)

            # s keys: request_id, user_id, item_key, cost, status, time
            data = {
                "request_id": s.get("request_id") or s.get("id") or s.get("req_id"),
                "user_id": uid,
                "user_name": uname,
                "item_key": s.get("item_key"),
                "cost": s.get("cost"),
                "time": s.get("time"),
            }
            results.append({"type": "shop", "data": data})

        return results
