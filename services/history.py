import datetime
from services.gsheet import GSheetService
from services.economy import EconomyService
from utils.cache import ranking_cache, user_stats_cache, activity_cache, cached


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
                status = (
                    row[idx_stat]
                    if idx_stat is not None and len(row) > idx_stat
                    else ""
                )

                # デバッグログ
                print(
                    f"[DEBUG STATS] user_id={row[idx_uid] if len(row) > idx_uid else 'N/A'}, duration_str='{duration_str}', status='{status}'"
                )

                if not duration_str.isdigit() or int(duration_str) == 0:
                    print(f"[DEBUG STATS] Skipped due to invalid duration")
                    continue

                duration = int(duration_str)
                date_str = row[idx_date] if len(row) > idx_date else ""
                # シングルクォートが先頭についている場合に除去（スプレッドシートの書式問題対策）
                date_str = date_str.lstrip("'").strip()
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

            # デバッグログ
            print(f"[DEBUG STATS] Final weekly_data: {weekly_data}")
            print(
                f"[DEBUG STATS] Total records found: {len(all_logs)}, total_minutes: {total_minutes}"
            )

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
    def get_user_study_stats_summary(user_id):
        """ユーザーの学習履歴統計（週間・月間の合計分数のみ）※カレンダー基準 - LINE Bot用"""
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
    @cached(ranking_cache, key_func=lambda: "study_time_ranking")
    def get_weekly_study_time_ranking():
        """過去7日間の勉強時間ランキング（科目別内訳付き）"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return []

        try:
            records = sheet.get_all_values()
            if len(records) <= 1:
                return []

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("display_name")
            idx_date = col_map.get("date")
            idx_dur = col_map.get("duration_min")
            idx_subj = col_map.get("subject")

            if None in [idx_uid, idx_date, idx_dur]:
                print("[DEBUG] Missing columns for study ranking")
                return []

            # 過去7日間の日付範囲
            today = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=9))
            ).date()
            week_start = today - datetime.timedelta(days=6)
            week_start_str = week_start.strftime("%Y-%m-%d")

            user_stats = {}  # {user_id: {total: int, subjects: {subject: minutes}, display_name: str}}

            for row in records[1:]:
                if len(row) <= idx_uid:
                    continue

                uid = str(row[idx_uid])
                date_str = row[idx_date] if len(row) > idx_date else ""
                # シングルクォート除去
                date_str = date_str.lstrip("'").strip()

                duration_str = row[idx_dur] if len(row) > idx_dur else "0"
                subject = (
                    row[idx_subj] if idx_subj and len(row) > idx_subj else "その他"
                )
                display_name = (
                    row[idx_name] if idx_name and len(row) > idx_name else uid
                )

                # 日付フィルタ
                if date_str < week_start_str:
                    continue

                # duration チェック
                if not duration_str.isdigit() or int(duration_str) == 0:
                    continue

                duration = int(duration_str)

                if uid not in user_stats:
                    user_stats[uid] = {
                        "total": 0,
                        "subjects": {},
                        "display_name": display_name,
                    }

                user_stats[uid]["total"] += duration
                if subject in user_stats[uid]["subjects"]:
                    user_stats[uid]["subjects"][subject] += duration
                else:
                    user_stats[uid]["subjects"][subject] = duration

                # display_nameを最新のものに更新
                if display_name and display_name != uid:
                    user_stats[uid]["display_name"] = display_name

            # ランキング作成
            ranking = []
            for uid, stats in user_stats.items():
                # 科目を分単位から時間に変換してソート
                subjects_list = [
                    {"subject": s, "minutes": m}
                    for s, m in sorted(
                        stats["subjects"].items(), key=lambda x: x[1], reverse=True
                    )
                ]
                ranking.append(
                    {
                        "user_id": uid,
                        "display_name": stats["display_name"],
                        "total_minutes": stats["total"],
                        "subjects": subjects_list,
                    }
                )

            # 勉強時間でソート
            ranking.sort(key=lambda x: x["total_minutes"], reverse=True)

            # 順位付け
            for i, r in enumerate(ranking):
                r["rank"] = i + 1

            return ranking

        except Exception as e:
            print(f"Weekly Study Ranking Error: {e}")
            import traceback

            traceback.print_exc()
            return []

    @staticmethod
    @cached(ranking_cache)
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
    @cached(activity_cache, key_func=lambda limit=10: f"recent_activity_{limit}")
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
                    idx_likes = col_map.get("likes")
                    idx_liked_by = col_map.get("liked_by")
                    idx_comments = col_map.get("comments")

                    import json

                    for row_index, row in enumerate(records[1:], start=2):
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
                            row[idx_comment]
                            if idx_comment and len(row) > idx_comment
                            else ""
                        )

                        # いいね・コメント情報
                        likes = (
                            int(row[idx_likes])
                            if idx_likes
                            and len(row) > idx_likes
                            and row[idx_likes].isdigit()
                            else 0
                        )
                        liked_by_str = (
                            row[idx_liked_by]
                            if idx_liked_by and len(row) > idx_liked_by
                            else "[]"
                        )
                        try:
                            liked_by = json.loads(liked_by_str) if liked_by_str else []
                        except:
                            liked_by = []
                        comments_count = (
                            int(row[idx_comments])
                            if idx_comments
                            and len(row) > idx_comments
                            and row[idx_comments].isdigit()
                            else 0
                        )

                        # タイムスタンプ用にdate + start_timeを結合
                        timestamp = f"{date} {start_time}" if start_time else date

                        recent_items.append(
                            {
                                "type": "study",
                                "row_index": row_index,  # いいね・コメント用
                                "user_name": name,
                                "description": f"{subject} {duration_str}分",
                                "comment": comment,
                                "timestamp": timestamp,
                                "icon": "📚",
                                "likes": likes,
                                "liked_by": liked_by,
                                "comments_count": comments_count,
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

    # ========== いいね・コメント機能 ==========

    @staticmethod
    def toggle_like(study_row_index, user_id):
        """勉強記録にいいねをトグル"""
        sheet = GSheetService.get_worksheet("study_log")
        if not sheet:
            return {"success": False, "message": "シートが見つかりません"}

        try:
            headers = sheet.row_values(1)
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_likes = col_map.get("likes")
            idx_liked_by = col_map.get("liked_by")

            # カラムがなければ追加（初回のみ）
            if idx_likes is None:
                idx_likes = len(headers)
                sheet.update_cell(1, idx_likes + 1, "likes")
            if idx_liked_by is None:
                idx_liked_by = len(headers) + (1 if idx_likes == len(headers) else 0)
                sheet.update_cell(1, idx_liked_by + 1, "liked_by")

            # 現在の値を取得
            row = sheet.row_values(study_row_index)
            current_likes = (
                int(row[idx_likes])
                if len(row) > idx_likes and row[idx_likes].isdigit()
                else 0
            )
            liked_by_str = row[idx_liked_by] if len(row) > idx_liked_by else "[]"

            import json

            try:
                liked_by = json.loads(liked_by_str) if liked_by_str else []
            except:
                liked_by = []

            # トグル処理
            if user_id in liked_by:
                liked_by.remove(user_id)
                current_likes = max(0, current_likes - 1)
                action = "unliked"
            else:
                liked_by.append(user_id)
                current_likes += 1
                action = "liked"

            # 更新
            sheet.update_cell(study_row_index, idx_likes + 1, current_likes)
            sheet.update_cell(study_row_index, idx_liked_by + 1, json.dumps(liked_by))

            return {
                "success": True,
                "action": action,
                "likes": current_likes,
                "liked_by": liked_by,
            }
        except Exception as e:
            print(f"Toggle Like Error: {e}")
            return {"success": False, "message": str(e)}

    @staticmethod
    def get_comments(study_row_index):
        """勉強記録のコメント一覧を取得"""
        sheet = GSheetService.get_worksheet("study_comments")
        if not sheet:
            return []

        try:
            records = sheet.get_all_values()
            if len(records) <= 1:
                return []

            headers = records[0]
            col_map = {str(h).strip(): i for i, h in enumerate(headers)}

            idx_row = col_map.get("study_row_index")
            idx_uid = col_map.get("user_id")
            idx_name = col_map.get("user_name")
            idx_comment = col_map.get("comment")
            idx_created = col_map.get("created_at")

            comments = []
            for row in records[1:]:
                if len(row) > idx_row and str(row[idx_row]) == str(study_row_index):
                    comments.append(
                        {
                            "user_id": row[idx_uid] if len(row) > idx_uid else "",
                            "user_name": row[idx_name] if len(row) > idx_name else "",
                            "comment": row[idx_comment]
                            if len(row) > idx_comment
                            else "",
                            "created_at": row[idx_created]
                            if len(row) > idx_created
                            else "",
                        }
                    )

            return comments
        except Exception as e:
            print(f"Get Comments Error: {e}")
            return []

    @staticmethod
    def add_comment(study_row_index, user_id, user_name, comment):
        """勉強記録にコメントを追加"""
        sheet = GSheetService.get_worksheet("study_comments")
        if not sheet:
            # シートがなければ作成
            try:
                doc = GSheetService.get_doc()
                sheet = doc.add_worksheet(title="study_comments", rows=100, cols=10)
                sheet.update(
                    "A1:E1",
                    [
                        [
                            "study_row_index",
                            "user_id",
                            "user_name",
                            "comment",
                            "created_at",
                        ]
                    ],
                )
            except Exception as e:
                print(f"Create Sheet Error: {e}")
                return {"success": False, "message": "シートを作成できませんでした"}

        try:
            now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
            created_at = now.strftime("%Y-%m-%d %H:%M:%S")

            sheet.append_row(
                [str(study_row_index), user_id, user_name, comment, created_at]
            )

            # study_logのコメント数も更新
            study_sheet = GSheetService.get_worksheet("study_log")
            if study_sheet:
                headers = study_sheet.row_values(1)
                col_map = {str(h).strip(): i for i, h in enumerate(headers)}
                idx_comments = col_map.get("comments")

                if idx_comments is None:
                    idx_comments = len(headers)
                    study_sheet.update_cell(1, idx_comments + 1, "comments")

                row = study_sheet.row_values(study_row_index)
                current_count = (
                    int(row[idx_comments])
                    if len(row) > idx_comments and row[idx_comments].isdigit()
                    else 0
                )
                study_sheet.update_cell(
                    study_row_index, idx_comments + 1, current_count + 1
                )

            return {"success": True, "created_at": created_at}
        except Exception as e:
            print(f"Add Comment Error: {e}")
            return {"success": False, "message": str(e)}
