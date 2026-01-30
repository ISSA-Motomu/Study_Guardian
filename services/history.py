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
            # get_all_records はヘッダー依存で不安定なため get_all_values を使用
            # 想定カラム: tx_id, user_id, amount, tx_type, related_id, timestamp, user_name
            rows = sheet.get_all_values()

            records = []
            # ヘッダー行判定 (1行目が "tx_id" ならヘッダーとみなす)
            start_index = 0
            if len(rows) > 0 and str(rows[0][0]) == "tx_id":
                start_index = 1

            for r in rows[start_index:]:
                if len(r) < 6:
                    continue

                records.append(
                    {
                        "tx_id": r[0],
                        "user_id": r[1],
                        "amount": int(r[2])
                        if r[2] and str(r[2]).lstrip("-").isdigit()
                        else 0,
                        "tx_type": r[3],
                        "related_id": r[4],
                        "timestamp": r[5],
                        "user_name": r[6] if len(r) > 6 else "",
                    }
                )

            # 新しい順にソート (timestamp降順)
            sorted_records = sorted(
                records, key=lambda x: str(x.get("timestamp", "")), reverse=True
            )
            return sorted_records
        except Exception as e:
            print(f"All History Error: {e}")
            return []

    @staticmethod
    def get_admin_history(limit=10):
        """管理用：最近の取引履歴を取得"""
        all_tx = HistoryService.get_all_transactions()
        return all_tx[:limit]

    @staticmethod
    def get_user_study_stats(user_id):
        """ユーザーの学習統計情報を収集（Web表示用）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return {"weekly": [], "subject": [], "recent": []}

        try:
            records = sheet.get_all_values()
            if not records:
                return {"weekly": [], "subject": [], "recent": []}

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_date = col_map.get("date")
            idx_dur = col_map.get("duration_min")
            idx_subj = col_map.get("subject")
            idx_stat = col_map.get("status")

            if None in [idx_uid, idx_date, idx_dur, idx_subj]:
                return {"weekly": [], "subject": [], "recent": []}

            # 7日間の日付リスト生成
            today = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=9))
            ).date()
            last_7_days = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
            weekly_map = {d.strftime("%Y-%m-%d"): 0 for d in last_7_days}
            days_jp = ["月", "火", "水", "木", "金", "土", "日"]

            subject_map = {}
            recent_logs = []

            for row in records[1:]:
                # User Filter
                if len(row) <= idx_uid or str(row[idx_uid]) != str(user_id):
                    continue

                # Status Filter (DONE or PENDING or updated ones which have duration)
                duration_str = row[idx_dur] if len(row) > idx_dur else "0"
                if not duration_str.isdigit() or int(duration_str) == 0:
                    continue

                duration = int(duration_str)
                date_str = row[idx_date] if len(row) > idx_date else ""
                subject = row[idx_subj] if len(row) > idx_subj else "その他"

                # Weekly Data
                if date_str in weekly_map:
                    weekly_map[date_str] += duration

                # Subject Data
                if subject in subject_map:
                    subject_map[subject] += duration
                else:
                    subject_map[subject] = duration

                # Recent Data (Keep all, sort later)
                recent_logs.append(
                    {"subject": subject, "date": date_str, "minutes": duration}
                )

            # Format Weekly Data
            weekly_data = []
            for d in last_7_days:
                d_str = d.strftime("%Y-%m-%d")
                weekday = days_jp[d.weekday()]
                weekly_data.append(
                    {"day": weekday, "date": d_str, "minutes": weekly_map[d_str]}
                )

            # Format Subject Data
            subject_data = []
            # Define colors
            colors = {
                "国語": "#FF6B6B",
                "数学": "#4D96FF",
                "英語": "#FFD93D",
                "理科": "#6BCB77",
                "社会": "#9D4EDD",
                "その他": "#95A5A6",
            }
            total_sub_min = sum(subject_map.values())
            for sub, mins in subject_map.items():
                subject_data.append(
                    {
                        "subject": sub,
                        "minutes": mins,
                        "color": colors.get(sub, "#95A5A6"),
                        "percent": (mins / total_sub_min * 100)
                        if total_sub_min > 0
                        else 0,
                    }
                )
            subject_data.sort(key=lambda x: x["minutes"], reverse=True)

            # Format Recent Data
            recent_logs.sort(key=lambda x: x["date"], reverse=True)
            all_logs = list(recent_logs)  # Keep all for weekly/monthly calc
            recent_logs = recent_logs[:10]  # Last 10 for display

            # Calculate total minutes
            total_minutes = sum(subject_map.values())

            return {
                "weekly": weekly_data,
                "subject": subject_data,
                "recent": recent_logs,
                "all_records": all_logs,  # For weekly/monthly subject breakdown
                "total": total_minutes,
            }

        except Exception as e:
            print(f"Stats Error: {e}")
            return {"weekly": [], "subject": [], "recent": []}

    @staticmethod
    def is_first_study_today(user_id):
        """その日の最初の勉強かどうか判定"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return False

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        today_str = now.strftime("%Y-%m-%d")

        # Resolve User Name for fallback
        user_name = None
        try:
            u_info = EconomyService.get_user_info(user_id)
            if u_info:
                user_name = u_info.get("display_name")
        except:
            pass

        try:
            records = sheet.get_all_values()
            if not records:
                return False

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_status = col_map.get("status")

            if idx_status is None or idx_date is None:
                return False

            count = 0
            for row in records[1:]:

                def get_val(idx):
                    return (
                        str(row[idx]).strip()
                        if idx is not None and idx < len(row)
                        else ""
                    )

                # ID Check
                is_match = False
                if idx_uid is not None and get_val(idx_uid) == str(user_id):
                    is_match = True
                elif (
                    user_name
                    and idx_name is not None
                    and get_val(idx_name) == str(user_name)
                ):
                    is_match = True

                if not is_match:
                    continue

                if get_val(idx_date) == today_str:
                    status = get_val(idx_status)
                    if status not in ["CANCELLED", "REJECTED"]:
                        count += 1

            # 今のセッションも含まれるため、1なら初回
            return count == 1

        except Exception as e:
            print(f"First Study Check Error: {e}")
            return False

    @staticmethod
    def get_today_study_count(user_id):
        """今日の勉強回数を取得"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return 0

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        today_str = now.strftime("%Y-%m-%d")

        # Resolve User Name for fallback
        user_name = None
        try:
            u_info = EconomyService.get_user_info(user_id)
            if u_info:
                user_name = u_info.get("display_name")
        except:
            pass

        try:
            records = sheet.get_all_values()
            if not records:
                return 0

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_status = col_map.get("status")

            if idx_status is None or idx_date is None:
                return 0

            count = 0
            for row in records[1:]:

                def get_val(idx):
                    return (
                        str(row[idx]).strip()
                        if idx is not None and idx < len(row)
                        else ""
                    )

                # ID Check
                is_match = False
                if idx_uid is not None and get_val(idx_uid) == str(user_id):
                    is_match = True
                elif (
                    user_name
                    and idx_name is not None
                    and get_val(idx_name) == str(user_name)
                ):
                    is_match = True

                if not is_match:
                    continue

                if get_val(idx_date) == today_str:
                    status = get_val(idx_status)
                    if status not in ["CANCELLED", "REJECTED"]:
                        count += 1
            return count
        except Exception as e:
            print(f"Study Count Error: {e}")
            return 0

    @staticmethod
    def get_user_study_stats(user_id):
        """ユーザーの学習履歴統計（週間・月間）※カレンダー基準"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return {"weekly": 0, "monthly": 0, "total": 0}

        now = datetime.datetime.now()
        # 今週の月曜日 (0:00:00)
        week_start = (now - datetime.timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # 今月の1日 (0:00:00)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        stats = {"weekly": 0, "monthly": 0, "total": 0}

        # Resolve User Name for fallback
        user_name = None
        try:
            u_info = EconomyService.get_user_info(user_id)
            if u_info:
                user_name = u_info.get("display_name")
        except:
            pass

        try:
            records = sheet.get_all_values()
            if not records:
                return stats

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_status = col_map.get("status")
            idx_dur = col_map.get("duration_min")

            if idx_status is None or idx_date is None or idx_dur is None:
                return stats

            for row in records[1:]:

                def get_val(idx):
                    return (
                        str(row[idx]).strip()
                        if idx is not None and idx < len(row)
                        else ""
                    )

                # ID Check
                is_match = False
                if idx_uid is not None and get_val(idx_uid) == str(user_id):
                    is_match = True
                elif (
                    user_name
                    and idx_name is not None
                    and get_val(idx_name) == str(user_name)
                ):
                    is_match = True

                if not is_match:
                    continue

                if get_val(idx_status) != "APPROVED":
                    continue  # 承認済みのみ

                date_str = get_val(idx_date)

                try:
                    log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")

                    minutes = 0
                    dur_val = get_val(idx_dur)
                    if dur_val and dur_val.isdigit():
                        minutes = int(dur_val)

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
    def get_user_weekly_daily_stats(user_id):
        """ユーザーの直近7日間の日別学習時間（教科別）"""
        now = datetime.datetime.now()
        # 今日を含む過去7日間
        dates = [(now - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
        weekdays = ["月", "火", "水", "木", "金", "土", "日"]

        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            # シートがない場合でも空のデータを返す
            return [
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "label": f"{d.month}/{d.day}({weekdays[d.weekday()]})",
                    "minutes": 0,
                    "subjects": {},
                }
                for d in dates
            ]

        # date_str keys: "YYYY-MM-DD"
        # Value structure: {"total": 0, "subjects": {"math": 0, "eng": 0, ...}}
        daily_map = {
            d.strftime("%Y-%m-%d"): {"total": 0, "subjects": {}} for d in dates
        }

        # Resolve Name
        user_name = None
        try:
            u = EconomyService.get_user_info(user_id)
            if u:
                user_name = u.get("display_name")
        except:
            pass

        try:
            records = sheet.get_all_values()
            if not records:
                raise Exception("No records")

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_status = col_map.get("status")
            idx_dur = col_map.get("duration_min")
            idx_subj = col_map.get("subject")

            for row in records[1:]:

                def get_val(idx):
                    return (
                        str(row[idx]).strip()
                        if idx is not None and idx < len(row)
                        else ""
                    )

                # ID Check
                is_match = False
                if idx_uid is not None and get_val(idx_uid) == str(user_id):
                    is_match = True
                elif (
                    user_name
                    and idx_name is not None
                    and get_val(idx_name) == str(user_name)
                ):
                    is_match = True

                if not is_match:
                    continue

                if idx_status is not None and get_val(idx_status) != "APPROVED":
                    continue

                if idx_date is None:
                    continue
                date_str = get_val(idx_date)

                if date_str in daily_map:
                    # Subject
                    subject = get_val(idx_subj) if idx_subj is not None else "その他"
                    if not subject:
                        subject = "その他"

                    try:
                        # Duration
                        minutes = 0
                        dur_val = get_val(idx_dur)
                        if dur_val and dur_val.isdigit():
                            minutes = int(dur_val)

                        daily_map[date_str]["total"] += minutes
                        if subject not in daily_map[date_str]["subjects"]:
                            daily_map[date_str]["subjects"][subject] = 0
                        daily_map[date_str]["subjects"][subject] += minutes
                    except:
                        pass
        except Exception as e:
            print(f"Daily Stats Error: {e}")

        # リスト形式に変換
        result = []
        for d in dates:
            d_str = d.strftime("%Y-%m-%d")
            data = daily_map[d_str]
            label = f"{d.month}/{d.day}({weekdays[d.weekday()]})"
            result.append(
                {
                    "date": d_str,
                    "label": label,
                    "minutes": data["total"],
                    "subjects": data["subjects"],
                }
            )
        return result

    @staticmethod
    def get_user_monthly_weekly_stats(user_id):
        """ユーザーの直近4週間の週別学習時間（教科別）"""
        now = datetime.datetime.now()
        # 過去4週間 (28日間)
        # 4つの期間を作る: [3週間前, 2週間前, 1週間前, 今週]
        weeks = []
        for i in range(3, -1, -1):
            # i=3: 21-27日前, i=0: 0-6日前
            end_d = now - datetime.timedelta(days=i * 7)
            start_d = end_d - datetime.timedelta(days=6)

            # 日付比較用にdateオブジェクトにする
            weeks.append(
                {
                    "start_date": start_d.date(),
                    "end_date": end_d.date(),
                    "label": f"{start_d.month}/{start_d.day}~",
                    "total": 0,
                    "subjects": {},
                }
            )

        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            # シートがない場合でも空のデータを返す
            result = []
            for w in weeks:
                result.append({"label": w["label"], "minutes": 0, "subjects": {}})
            return result

        # Resolve Name
        user_name = None
        try:
            u = EconomyService.get_user_info(user_id)
            if u:
                user_name = u.get("display_name")
        except:
            pass

        try:
            records = sheet.get_all_values()
            if not records:
                raise Exception("No records")

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_status = col_map.get("status")
            idx_dur = col_map.get("duration_min")
            idx_subj = col_map.get("subject")

            for row in records[1:]:

                def get_val(idx):
                    return (
                        str(row[idx]).strip()
                        if idx is not None and idx < len(row)
                        else ""
                    )

                # ID Check
                is_match = False
                if idx_uid is not None and get_val(idx_uid) == str(user_id):
                    is_match = True
                elif (
                    user_name
                    and idx_name is not None
                    and get_val(idx_name) == str(user_name)
                ):
                    is_match = True

                if not is_match:
                    continue

                if idx_status is not None and get_val(idx_status) != "APPROVED":
                    continue

                if idx_date is None:
                    continue
                date_str = get_val(idx_date)

                try:
                    log_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

                    # どの週に該当するかチェック
                    target_week = None
                    for w in weeks:
                        if w["start_date"] <= log_date <= w["end_date"]:
                            target_week = w
                            break

                    if target_week:
                        subject = (
                            get_val(idx_subj) if idx_subj is not None else "その他"
                        )
                        if not subject:
                            subject = "その他"

                        # Duration
                        minutes = 0
                        dur_val = get_val(idx_dur)
                        if dur_val and dur_val.isdigit():
                            minutes = int(dur_val)

                        target_week["total"] += minutes
                        if subject not in target_week["subjects"]:
                            target_week["subjects"][subject] = 0
                        target_week["subjects"][subject] += minutes

                except:
                    pass
        except Exception as e:
            print(f"Monthly Stats Error: {e}")

        # 結果整形
        result = []
        for w in weeks:
            result.append(
                {"label": w["label"], "minutes": w["total"], "subjects": w["subjects"]}
            )

        return result

    @staticmethod
    def get_user_job_history(user_id, limit=5):
        """ユーザーの完了したジョブ履歴"""
        sheet = GSheetService.get_worksheet("jobs")
        if not sheet:
            return []

        jobs = []
        try:
            rows = sheet.get_all_values()
            if len(rows) > 1:
                # Header: job_id, title, reward, status, client_id, worker_id, deadline
                for r in rows[1:]:
                    if len(r) < 6:
                        continue

                    # Check worker_id (F=5) and status (D=3)
                    if str(r[5]) == user_id and str(r[3]) == "CLOSED":
                        jobs.append(
                            {
                                "job_id": r[0],
                                "title": r[1],
                                "reward": r[2],
                                "status": r[3],
                                "client_id": r[4],
                                "worker_id": r[5],
                                "deadline": r[6] if len(r) > 6 else "",
                            }
                        )

            # Sort by job_id desc
            sorted_jobs = sorted(jobs, key=lambda x: x.get("job_id", ""), reverse=True)
            return sorted_jobs[:limit]
        except Exception as e:
            print(f"Job History Error: {e}")
            return []

    @staticmethod
    def get_user_job_count(user_id):
        """ユーザーの完了したジョブ総数"""
        sheet = GSheetService.get_worksheet("jobs")
        if not sheet:
            return 0

        try:
            rows = sheet.get_all_values()
            count = 0
            if len(rows) > 1:
                for r in rows[1:]:
                    if len(r) < 6:
                        continue
                    if str(r[5]) == user_id and str(r[3]) == "CLOSED":
                        count += 1
            return count
        except Exception as e:
            print(f"Job Count Error: {e}")
            return 0

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

    @staticmethod
    def get_weekly_exp_ranking():
        """今週の獲得EXPランキング（USERのみ）"""
        sheet = GSheetService.get_worksheet("transactions")
        if not sheet:
            return []

        now = datetime.datetime.now()
        week_start = now - datetime.timedelta(days=7)

        user_exp = {}  # {user_id: total_exp}

        try:
            records = sheet.get_all_records()
            for tx in records:
                # tx: tx_id, user_id, amount, tx_type, related_id, timestamp
                if tx.get("tx_type") != "REWARD":
                    continue

                ts_str = str(tx.get("timestamp"))
                try:
                    # フォーマットは "YYYY-MM-DD HH:MM:SS"
                    tx_date = datetime.datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                except:
                    continue

                if tx_date < week_start:
                    continue

                uid = str(tx.get("user_id"))
                amount = int(tx.get("amount", 0))
                user_exp[uid] = user_exp.get(uid, 0) + amount

            # ユーザー情報と結合してフィルタリング
            all_users = EconomyService.get_all_users()

            # Admin IDを特定 (重複エントリ対策: どこかにADMINがあればそのIDはAdminとみなす)
            admin_ids = set()
            for u in all_users:
                if str(u.get("role", "")).strip().upper() == "ADMIN":
                    admin_ids.add(str(u.get("user_id")))

            ranking = []

            for u in all_users:
                uid = str(u.get("user_id"))

                # Adminとして特定されたIDはスキップ
                if uid in admin_ids:
                    continue

                role = str(u.get("role", "")).strip().upper()
                if role != "USER":
                    continue

                earned = user_exp.get(uid, 0)
                ranking.append(
                    {
                        "user_id": uid,
                        "display_name": u.get("display_name"),
                        "weekly_exp": earned,
                        "total_study_time": u.get("total_study_time", 0),
                        "user_rank": u.get("rank", "E"),  # シートのランク情報を追加
                    }
                )

            # ソート
            ranking.sort(key=lambda x: x["weekly_exp"], reverse=True)

            # 順位付け
            for i, r in enumerate(ranking):
                r["rank"] = i + 1

            return ranking

        except Exception as e:
            print(f"Weekly Ranking Error: {e}")
            return []

    @staticmethod
    def get_all_recent_activity(limit=10):
        """全ユーザーの最近の勉強・お手伝い履歴を取得"""
        recent_items = []

        # 1) 勉強履歴を取得
        try:
            study_sheet = GSheetService.get_worksheet("study_log")
            if study_sheet:
                records = study_sheet.get_all_values()
                if len(records) > 1:
                    headers = records[0]
                    col_map = {str(h).strip(): i for i, h in enumerate(headers)}

                    idx_name = col_map.get("display_name")
                    idx_date = col_map.get("date")
                    idx_dur = col_map.get("duration_min")
                    idx_subj = col_map.get("subject")
                    idx_stat = col_map.get("status")
                    idx_time = col_map.get("start_time")
                    idx_comment = col_map.get("comment")

                    for row in records[1:]:
                        # APPROVED または DONE のもののみ
                        status = (
                            row[idx_stat] if idx_stat and len(row) > idx_stat else ""
                        )
                        if status.upper() not in ["APPROVED", "DONE"]:
                            continue

                        duration_str = (
                            row[idx_dur] if idx_dur and len(row) > idx_dur else "0"
                        )
                        if not duration_str.isdigit() or int(duration_str) == 0:
                            continue

                        name = (
                            row[idx_name]
                            if idx_name and len(row) > idx_name
                            else "Unknown"
                        )
                        date = row[idx_date] if idx_date and len(row) > idx_date else ""
                        subject = (
                            row[idx_subj] if idx_subj and len(row) > idx_subj else ""
                        )
                        start_time = (
                            row[idx_time] if idx_time and len(row) > idx_time else ""
                        )
                        comment = (
                            row[idx_comment] if idx_comment and len(row) > idx_comment else ""
                        )

                        # タイムスタンプ用にdate + start_timeを結合
                        timestamp = f"{date} {start_time}" if start_time else date

                        recent_items.append(
                            {
                                "type": "study",
                                "user_name": name,
                                "description": f"{subject} {duration_str}分",
                                "comment": comment,
                                "timestamp": timestamp,
                                "icon": "📚",
                            }
                        )
        except Exception as e:
            print(f"Study Activity Error: {e}")

        # 2) お手伝い(ジョブ)履歴を取得（jobsシートを参照）
        try:
            job_sheet = GSheetService.get_worksheet("jobs")
            if job_sheet:
                records = job_sheet.get_all_values()
                if len(records) > 1:
                    headers = records[0]
                    col_map = {str(h).strip(): i for i, h in enumerate(headers)}

                    idx_worker = col_map.get("worker_id")
                    idx_title = col_map.get("title")
                    idx_stat = col_map.get("status")
                    idx_time = col_map.get("finished_at")

                    for row in records[1:]:
                        status = (
                            row[idx_stat] if idx_stat and len(row) > idx_stat else ""
                        )
                        # CLOSEDのジョブのみ表示（完了済み）
                        if status.upper() != "CLOSED":
                            continue

                        # worker_idからユーザー名を取得
                        worker_id = (
                            row[idx_worker]
                            if idx_worker and len(row) > idx_worker
                            else ""
                        )
                        # ユーザー名を取得
                        try:
                            user_info = EconomyService.get_user_info(worker_id)
                            name = (
                                user_info.get("display_name", "Unknown")
                                if user_info
                                else "Unknown"
                            )
                        except:
                            name = "Unknown"

                        title = (
                            row[idx_title]
                            if idx_title and len(row) > idx_title
                            else "お手伝い"
                        )
                        timestamp = (
                            row[idx_time] if idx_time and len(row) > idx_time else ""
                        )

                        recent_items.append(
                            {
                                "type": "job",
                                "user_name": name,
                                "description": title,
                                "timestamp": timestamp,
                                "icon": "🏠",
                            }
                        )
        except Exception as e:
            print(f"Job Activity Error: {e}")

        # 3) タイムスタンプでソートして最新をlimit件返す
        recent_items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return recent_items[:limit]
