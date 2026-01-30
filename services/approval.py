from services.gsheet import GSheetService
from services.job import JobService
from services.shop import ShopService
from services.economy import EconomyService
from services.mission import MissionService
from utils.cache import pending_cache, cached


class ApprovalService:
    @staticmethod
    @cached(pending_cache)
    def get_all_pending():
        """全ての承認待ち項目をフラットなリストで取得"""
        results = []

        # ユーザー名解決用のマッピング作成
        users = EconomyService.get_all_users()
        user_map = {str(u.get("user_id")): u.get("display_name") for u in users}

        # 1. 勉強記録
        studies = GSheetService.get_pending_studies()
        for s in studies:
            # s keys: row_index, user_id, user_name, date, start_time, end_time, subject, comment
            uid = str(s.get("user_id", ""))
            saved_name = s.get("user_name") or s.get("display_name")
            uname = saved_name if saved_name else user_map.get(uid, uid)

            # 勉強時間を計算
            minutes = 0
            try:
                start = s.get("start_time", "")
                end = s.get("end_time", "")
                if start and end:
                    from datetime import datetime

                    start_dt = datetime.strptime(start, "%H:%M:%S")
                    end_dt = datetime.strptime(end, "%H:%M:%S")
                    diff = end_dt - start_dt
                    minutes = max(0, int(diff.total_seconds() / 60))
            except:
                pass

            data = {
                "row_index": s.get("row_index"),
                "user_id": uid,
                "user_name": uname,
                "date": s.get("date", ""),
                "start_time": s.get("start_time", ""),
                "end_time": s.get("end_time", ""),
                "subject": s.get("subject", "勉強"),
                "comment": s.get("comment", ""),
                "minutes": minutes,
            }
            results.append({"type": "study", "data": data})

        # 2. ジョブ完了報告
        jobs = JobService.get_pending_reviews()
        for j in jobs:
            worker_id = str(j.get("worker_id", ""))
            worker_name = user_map.get(worker_id, worker_id)

            data = {
                "job_id": j.get("job_id"),
                "user_id": worker_id,
                "worker_id": worker_id,
                "user_name": worker_name,
                "worker_name": worker_name,
                "title": j.get("title", "お手伝い"),
                "description": j.get("description", ""),
                "reward": j.get("reward", 0),
                "comment": j.get("comment", ""),
                "created_at": j.get("created_at", ""),
                "finished_at": j.get("finished_at", ""),
            }
            results.append({"type": "job", "data": data})

        # 3. ショップ購入リクエスト
        shops = ShopService.get_pending_requests()
        # アイテム名取得用
        shop_items = ShopService.get_items()

        for s in shops:
            uid = str(s.get("user_id", ""))
            saved_name = s.get("user_name") or s.get("display_name")
            uname = saved_name if saved_name else user_map.get(uid, uid)

            time_val = s.get("time") or s.get("timestamp") or s.get("created_at") or ""
            item_key = s.get("item_key", "")
            item_name = (
                shop_items.get(item_key, {}).get("name", item_key)
                if shop_items
                else item_key
            )

            # request_id を取得（req_id や id もフォールバックとして使用）
            req_id = s.get("request_id") or s.get("req_id") or s.get("id") or ""
            if not req_id:
                # ログを出さずにスキップ（古いデータは無視）
                continue

            data = {
                "request_id": req_id,
                "user_id": uid,
                "user_name": uname,
                "item_key": item_key,
                "item_name": item_name,
                "cost": s.get("cost", 0),
                "created_at": time_val,
            }
            results.append({"type": "shop", "data": data})

        # 4. ミッション完了報告
        missions = MissionService.get_pending_reviews()
        for m in missions:
            uid = str(m.get("user_id", ""))
            uname = user_map.get(uid, uid)

            data = {
                "mission_id": m.get("mission_id"),
                "user_id": uid,
                "user_name": uname,
                "title": m.get("title", "ミッション"),
                "description": m.get("description", ""),
                "reward": m.get("reward", 0),
                "created_at": m.get("created_at", ""),
            }
            results.append({"type": "mission", "data": data})

        return results
