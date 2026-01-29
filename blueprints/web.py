from flask import Blueprint, jsonify, request, send_from_directory, current_app
import os
import datetime
from services.job import JobService
from services.shop import ShopService
from services.gsheet import GSheetService
from services.economy import EconomyService
from services.history import HistoryService
from services.status_service import StatusService
from services.stats import SagaStats
from bot_instance import line_bot_api
from utils.template_loader import load_template
from linebot.models import FlexSendMessage, TextSendMessage
from handlers import study
from utils.achievements import AchievementManager, ACHIEVEMENT_MASTER

web_bp = Blueprint("web", __name__)


@web_bp.route("/api/admin/users")
def api_admin_users():
    """全ユーザーリストを返す"""
    users = EconomyService.get_all_users()
    # フロントエンドで使いやすい形式に整形
    user_list = []
    for u in users:
        user_list.append(
            {"user_id": u.get("user_id"), "user_name": u.get("display_name", "Unknown")}
        )
    return jsonify({"status": "success", "users": user_list})


@web_bp.route("/api/admin/add_task", methods=["POST"])
def api_admin_add_task():
    """タスク追加"""
    data = request.json
    title = data.get("title")
    reward = data.get("reward")
    # client_id = data.get("user_id") # 未使用のためコメントアウト

    if not title:
        return jsonify({"status": "error", "message": "Title required"}), 400

    # JobService.add_jobを使用するように修正（create_jobは前回までの実装か誤記）
    success, msg = JobService.add_job(title, reward)
    if success:
        return jsonify({"status": "success", "job_id": msg})
    else:
        return jsonify({"status": "error", "message": msg}), 500


@web_bp.route("/api/admin/add_item", methods=["POST"])
def api_admin_add_item():
    """アイテム追加"""
    data = request.json
    name = data.get("name")
    cost = data.get("cost")
    description = data.get("description", "")

    if not name:
        return jsonify({"status": "error", "message": "Name required"}), 400

    if ShopService.add_item(name, cost, description):
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Failed to add item"}), 500


@web_bp.route("/api/admin/grant_points", methods=["POST"])
def api_admin_grant_points():
    """ポイント付与"""
    data = request.json
    user_id = data.get("user_id")
    amount = data.get("amount")

    if not user_id or amount is None:
        return jsonify({"status": "error", "message": "Missing params"}), 400

    if EconomyService.add_exp(user_id, int(amount), "ADMIN_GRANT"):
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Failed to grant"}), 500


@web_bp.route("/app/dashboard")
def liff_dashboard():
    """LIFFのトップページ (ダッシュボード) を返す"""
    # Vueでビルドされた静的ファイルを返す
    directory = os.path.join(current_app.root_path, "static", "dist")
    if not os.path.exists(directory):
        # ビルド前の場合のフォールバック (またはエラー表示)
        # 開発中は旧画面を出すか、ビルドを促すメッセージを出す
        return (
            "Frontend not built. Please run 'npm run build' in frontend directory.",
            503,
        )
    return send_from_directory(directory, "index.html")


@web_bp.route("/api/user/update_profile", methods=["POST"])
def api_update_profile():
    """LIFFから取得した最新のプロフィール情報でDBを更新する"""
    data = request.json
    user_id = data.get("user_id")
    display_name = data.get("display_name")
    avatar_url = data.get("avatar_url")

    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id"}), 400

    # ユーザーが存在するか確認、いなければ登録フローが必要だが
    # LIFFが開けている時点で登録済みか、もしくはここで登録してもよいが
    # 基本は登録済みのはず。

    if EconomyService.update_user_profile(user_id, display_name, avatar_url):
        return jsonify({"status": "ok"})
    else:
        # 更新失敗（ユーザーがいない場合など）
        # 新規登録を試みる？ 今回はシンプルにエラーもしくは無視
        return jsonify({"status": "error", "message": "Update failed"}), 500


@web_bp.route("/api/user/<user_id>/status")
def api_user_status(user_id):
    """ユーザーのステータス情報をJSONで返すAPI"""
    try:
        user_info = EconomyService.get_user_info(user_id)
        if not user_info:
            return jsonify({"status": "error", "message": "User not found"}), 404

        study_stats = HistoryService.get_user_study_stats(user_id)

        total_minutes = study_stats.get("total", 0)
        total_hours = total_minutes / 60

        # ランク判定には分を使用
        rank_info = StatusService.get_rank_info(total_minutes)

        # レベル計算 (例: 1時間でレベルアップ)
        level = int(total_hours) + 1

        # 次のレベルまでの経験値 (次の時間までの残り分数など)
        # ここでは簡易的に 1時間 = 100 EXP として表現
        exp = int((total_minutes % 60) / 60 * 100)
        next_exp = 100

        response_data = {
            "name": user_info.get("display_name", "Unknown"),
            "level": level,
            "exp": exp,
            "next_exp": next_exp,
            "xp": int(
                user_info.get("current_exp", 0)
            ),  # シートのcurrent_expを通貨XPとして扱う
            "gems": 0,  # ジェムは一先ず0固定
            "total_hours": round(total_hours, 1),
            "rank_name": rank_info.get("name", "Rank E"),
            "avatar_url": user_info.get("avatar_url", ""),
            "role": user_info.get("role", "USER"),
        }

        return jsonify({"status": "ok", "data": response_data})

    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/study/subjects")
def api_study_subjects():
    """学習可能な科目リストと色定義を返す"""
    return jsonify({"status": "ok", "data": study.SUBJECT_COLORS})


@web_bp.route("/api/shop/items")
def api_shop_items():
    """ショップの商品リストを返す"""
    items = ShopService.get_items()
    # OrderedDict to list
    items_list = []
    for key, val in items.items():
        val["key"] = key
        items_list.append(val)
    return jsonify({"status": "ok", "data": items_list})


@web_bp.route("/api/shop/buy", methods=["POST"])
def api_shop_buy():
    """商品購入リクエスト"""
    data = request.json
    user_id = data.get("user_id")
    item_key = data.get("item_key")
    comment = data.get("comment", "")

    if not user_id or not item_key:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    items = ShopService.get_items()
    item = items.get(item_key)
    if not item:
        return jsonify({"status": "error", "message": "Item not found"}), 404

    cost = item["cost"]

    # 残高チェック
    if not EconomyService.check_balance(user_id, cost):
        return jsonify({"status": "error", "message": "Not enough coins"}), 400

    # ポイント減算
    EconomyService.add_exp(user_id, -cost, f"BUY_{item_key}")

    # リクエスト作成
    user_info = EconomyService.get_user_info(user_id)
    user_name = user_info.get("display_name", "Unknown") if user_info else "Unknown"

    ShopService.create_request(user_id, item_key, cost, comment, user_name)

    # TODO: AdminへのLINE通知などもここで行うと親切

    return jsonify({"status": "ok", "message": "Requested"})


@web_bp.route("/api/study/start", methods=["POST"])
def api_start_study():
    """学習セッションを開始する"""
    data = request.json
    user_id = data.get("user_id")
    subject = data.get("subject")

    if not user_id or not subject:
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

    try:
        user_info = EconomyService.get_user_info(user_id)
        user_name = user_info["display_name"] if user_info else "User"

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")

        if GSheetService.log_activity(user_id, user_name, today, current_time, subject):
            color = study.SUBJECT_COLORS.get(subject, "#27ACB2")
            try:
                bubble = load_template(
                    "study_session.json",
                    subject=subject,
                    start_time=current_time,
                    color=color,
                )
                line_bot_api.push_message(
                    user_id,
                    FlexSendMessage(alt_text="勉強中...", contents=bubble),
                )
            except Exception as push_error:
                print(f"Push Message Error: {push_error}")
                # LINE通知失敗でも処理は継続する

            return jsonify({"status": "ok", "start_time": current_time})
        else:
            return jsonify(
                {"status": "error", "message": "Failed to log activity"}
            ), 500

    except Exception as e:
        print(f"Study Start Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/user/<user_id>/active_session")
def api_user_active_session(user_id):
    """ユーザーのアクティブな勉強セッションを確認"""
    try:
        session = GSheetService.get_user_active_session(user_id)
        if session:
            return jsonify({"status": "ok", "active": True, "data": session})
        return jsonify({"status": "ok", "active": False})
    except Exception as e:
        print(f"Active Session Check Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/user/<user_id>/stats")
def api_user_stats(user_id):
    """ユーザーの学習統計詳細を取得"""
    try:
        stats = HistoryService.get_user_study_stats(user_id)
        # weekly, subject, recent, total が含まれる
        return jsonify(stats)
    except Exception as e:
        print(f"Stats API Error: {e}")
        return jsonify({"weekly": [], "subject": [], "recent": [], "total": 0})


@web_bp.route("/api/study/finish", methods=["POST"])
def api_finish_study():
    data = request.json
    user_id = data.get("user_id")
    # Memo from frontend corresponds to Comment
    memo = data.get("memo", "なし")
    # Concentration not in frontend yet, default to 3
    concentration = 3

    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    current_time = now.strftime("%H:%M:%S")

    user_info = EconomyService.get_user_info(user_id)
    user_name = user_info["display_name"] if user_info else "User"

    # 1. Update End Time & Status to PENDING
    result = GSheetService.update_end_time(user_id, current_time, user_name)
    if not result:
        return jsonify(
            {
                "status": "error",
                "message": "Failed to update end time or no active session",
            }
        ), 404

    row_index = result["row_index"]
    start_time_str = result.get("start_time", "")
    subject = result.get("subject", "")

    # 2. Save Details (Memo/Concentration)
    try:
        GSheetService.update_study_details(row_index, memo, concentration)
    except Exception as e:
        print(f"Details update error: {e}")

    try:
        # 3. Calculate Duration
        start_dt = datetime.datetime.strptime(start_time_str, "%H:%M:%S")
        end_dt = datetime.datetime.strptime(current_time, "%H:%M:%S")
        if end_dt < start_dt:
            end_dt += datetime.timedelta(days=1)
        duration = end_dt - start_dt
        minutes = int(duration.total_seconds() / 60)

        # Cap at 90 mins
        if minutes > 90:
            minutes = 90

        earned_exp = minutes

        # 4. Update Stats (Rank/Duration)
        stats = SagaStats.calculate(minutes)
        if stats:
            GSheetService.update_study_stats(row_index, minutes, stats["rank"])

        # 5. Bonus Calculation
        bonus_msg = ""
        is_first_today = HistoryService.is_first_study_today(user_id)
        if minutes >= 5 and is_first_today:
            bonus = 30
            earned_exp += bonus
            bonus_msg = f"\n🎁 初回ボーナス: +{bonus}pt"

        # 6. Achievements Check
        achievement_msg = ""
        try:
            if user_info:
                current_session = {
                    "start_time": start_time_str,
                    "minutes": minutes,
                    "is_first_ever": int(user_info.get("total_study_time", 0)) == 0,
                }
                new_achievements = AchievementManager.check_achievements(
                    user_info, current_session
                )
                if new_achievements:
                    current_str = str(user_info.get("unlocked_achievements", ""))
                    new_ids = [a.value for a in new_achievements]
                    current_set = set(current_str.split(",")) if current_str else set()
                    for nid in new_ids:
                        current_set.add(nid)
                    updated_str = ",".join(list(current_set))
                    EconomyService.update_user_achievements(user_id, updated_str)

                    ach_titles = [ACHIEVEMENT_MASTER[a].title for a in new_achievements]
                    achievement_msg = f"\n\n🎉 実績解除！\n" + "\n".join(
                        [f"・{t}" for t in ach_titles]
                    )
        except Exception as e:
            print(f"Achievement Error: {e}")

        # 7. Notify User
        hours, mins = divmod(minutes, 60)
        subject_str = f"\n教科: {subject}" if subject else ""
        stats_msg = ""
        if stats:
            stats_msg = f"\n\n📊 佐賀県統計モデル\n偏差値: {stats['deviation']}\n判定: {stats['school_level']}"
            if stats.get("is_saganishi"):
                stats_msg += "\n🌸 佐賀西合格圏内！"

        try:
            line_bot_api.push_message(
                user_id,
                TextSendMessage(
                    text=f"OK！Webから記録したよ✨\n勉強時間: {hours}時間{mins}分{subject_str}\n成果: {memo}\n集中度: {concentration}/5{bonus_msg}{achievement_msg}{stats_msg}\n\n親御さんに報告しておいたからね！"
                ),
            )
        except Exception as push_err:
            print(f"User Push Error: {push_err}")

        # 8. Notify Admins
        try:
            admins = EconomyService.get_admin_users()
            admin_ids = [str(u["user_id"]) for u in admins if u.get("user_id")]

            if admin_ids:
                timestamp_str = now.strftime("%H:%M")
                approve_flex = load_template(
                    "study_approve_request.json",
                    user_name=user_name,
                    subject=subject,
                    hours=hours,
                    mins=mins,
                    minutes=minutes,
                    earned_exp=earned_exp,
                    user_id=user_id,
                    comment=memo + bonus_msg,
                    concentration=concentration,
                    timestamp=timestamp_str,
                    row_index=row_index,
                )
                line_bot_api.multicast(
                    admin_ids,
                    FlexSendMessage(alt_text="勉強完了報告", contents=approve_flex),
                )
        except Exception as admin_err:
            print(f"Admin Notify Error: {admin_err}")

        return jsonify({"status": "ok", "minutes": minutes})

    except Exception as e:
        print(f"Finish Process Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/study/cancel", methods=["POST"])
def api_cancel_study():
    data = request.json
    user_id = data.get("user_id")

    if GSheetService.cancel_study(user_id):
        return jsonify({"status": "ok"})
    return jsonify({"status": "error", "message": "Failed to cancel"}), 400


# ===== Evolution Game API =====
@web_bp.route("/api/game/evolution/<user_id>")
def api_get_evolution(user_id):
    """進化ゲームのデータを取得"""
    try:
        sheet = GSheetService.get_worksheet("evolution_data")
        if not sheet:
            return jsonify({"status": "ok", "data": None})

        records = sheet.get_all_values()
        if len(records) <= 1:
            return jsonify({"status": "ok", "data": None})

        headers = records[0]
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_uid = col_map.get("user_id")
        idx_kp = col_map.get("knowledge_points")
        idx_total = col_map.get("total_earned")
        idx_levels = col_map.get("facility_levels")

        for row in records[1:]:
            if len(row) > idx_uid and str(row[idx_uid]) == str(user_id):
                import json

                levels_str = (
                    row[idx_levels]
                    if idx_levels is not None and idx_levels < len(row)
                    else "{}"
                )
                try:
                    levels = json.loads(levels_str) if levels_str else {}
                except:
                    levels = {}

                return jsonify(
                    {
                        "status": "ok",
                        "data": {
                            "knowledge_points": int(row[idx_kp])
                            if idx_kp is not None and row[idx_kp]
                            else 0,
                            "total_earned": int(row[idx_total])
                            if idx_total is not None and row[idx_total]
                            else 0,
                            "facility_levels": levels,
                        },
                    }
                )

        return jsonify({"status": "ok", "data": None})

    except Exception as e:
        print(f"Evolution Get Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/game/evolution/sync", methods=["POST"])
def api_sync_evolution():
    """進化ゲームのデータを同期（保存）"""
    import json

    data = request.json
    user_id = data.get("user_id")
    knowledge_points = data.get("knowledge_points", 0)
    total_earned = data.get("total_earned", 0)
    facility_levels = data.get("facility_levels", {})

    try:
        sheet = GSheetService.get_worksheet("evolution_data")
        if not sheet:
            # シートがない場合は新規作成
            spreadsheet = GSheetService.get_spreadsheet()
            if spreadsheet:
                sheet = spreadsheet.add_worksheet(
                    title="evolution_data", rows=100, cols=10
                )
                sheet.append_row(
                    [
                        "user_id",
                        "knowledge_points",
                        "total_earned",
                        "facility_levels",
                        "last_sync",
                    ]
                )

        if not sheet:
            return jsonify({"status": "error", "message": "Cannot access sheet"}), 500

        records = sheet.get_all_values()
        headers = (
            records[0]
            if records
            else [
                "user_id",
                "knowledge_points",
                "total_earned",
                "facility_levels",
                "last_sync",
            ]
        )
        col_map = {str(h).strip(): i for i, h in enumerate(headers)}

        idx_uid = col_map.get("user_id", 0)
        idx_kp = col_map.get("knowledge_points", 1)
        idx_total = col_map.get("total_earned", 2)
        idx_levels = col_map.get("facility_levels", 3)
        idx_sync = col_map.get("last_sync", 4)

        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        levels_json = json.dumps(facility_levels)

        # 既存ユーザーを探す
        target_row = None
        for i, row in enumerate(records[1:], start=2):
            if len(row) > idx_uid and str(row[idx_uid]) == str(user_id):
                target_row = i
                break

        if target_row:
            # 更新
            sheet.update_cell(target_row, idx_kp + 1, knowledge_points)
            sheet.update_cell(target_row, idx_total + 1, total_earned)
            sheet.update_cell(target_row, idx_levels + 1, levels_json)
            sheet.update_cell(target_row, idx_sync + 1, timestamp)
        else:
            # 新規追加
            new_row = [""] * max(5, len(headers))
            new_row[idx_uid] = user_id
            new_row[idx_kp] = knowledge_points
            new_row[idx_total] = total_earned
            new_row[idx_levels] = levels_json
            new_row[idx_sync] = timestamp
            sheet.append_row(new_row)

        return jsonify({"status": "ok"})

    except Exception as e:
        print(f"Evolution Sync Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/study/pause", methods=["POST"])
def api_pause_study():
    data = request.json
    user_id = data.get("user_id")
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    current_time = now.strftime("%H:%M:%S")

    result = GSheetService.update_end_time(user_id, current_time)
    if result:
        return jsonify({"status": "ok"})
    return jsonify({"status": "error"}), 400


# ===== ADMIN API =====


@web_bp.route("/api/admin/pending")
def api_admin_pending():
    """承認待ちの全項目を取得"""
    from services.approval import ApprovalService

    try:
        pending_items = ApprovalService.get_all_pending()
        return jsonify({"status": "ok", "data": pending_items})
    except Exception as e:
        print(f"Admin Pending Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/approve/study", methods=["POST"])
def api_admin_approve_study():
    """勉強記録を承認"""
    data = request.json
    print(f"[DEBUG] approve_study received: {data}")
    row_index = data.get("row_index")
    user_id = data.get("user_id")
    minutes = data.get("minutes", 0)

    if not row_index:
        print(f"[DEBUG] Missing row_index in data: {data}")
        return jsonify({"status": "error", "message": "Missing row_index"}), 400

    try:
        # 承認処理
        print(f"[DEBUG] Calling approve_study with row_index={row_index}")
        if GSheetService.approve_study(int(row_index)):
            # EXP付与
            earned_exp = int(minutes) if minutes else 0
            if earned_exp > 0 and user_id:
                EconomyService.add_exp(user_id, earned_exp, "STUDY_APPROVED")
                # 累計勉強時間も更新
                EconomyService.add_study_time(user_id, earned_exp)

            # ユーザーに通知
            if user_id:
                try:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(
                            text=f"✅ 勉強記録が承認されました！\n+{earned_exp} XP 獲得！"
                        ),
                    )
                except:
                    pass

            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": "Failed to approve"}), 500
    except Exception as e:
        print(f"Approve Study Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/reject/study", methods=["POST"])
def api_admin_reject_study():
    """勉強記録を却下"""
    data = request.json
    row_index = data.get("row_index")
    user_id = data.get("user_id")

    if not row_index:
        return jsonify({"status": "error", "message": "Missing row_index"}), 400

    try:
        if GSheetService.reject_study(int(row_index)):
            # ユーザーに通知
            if user_id:
                try:
                    line_bot_api.push_message(
                        user_id,
                        TextSendMessage(
                            text="❌ 勉強記録が却下されました。\n記録に問題があった可能性があります。"
                        ),
                    )
                except:
                    pass
            return jsonify({"status": "ok"})
        else:
            return jsonify({"status": "error", "message": "Failed to reject"}), 500
    except Exception as e:
        print(f"Reject Study Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/approve/job", methods=["POST"])
def api_admin_approve_job():
    """ジョブ完了を承認"""
    from services.job import JobService

    data = request.json
    job_id = data.get("job_id")

    if not job_id:
        return jsonify({"status": "error", "message": "Missing job_id"}), 400

    try:
        success, msg = JobService.approve_job(job_id)
        if success:
            return jsonify({"status": "ok", "message": msg})
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        print(f"Approve Job Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/reject/job", methods=["POST"])
def api_admin_reject_job():
    """ジョブ完了を却下"""
    from services.job import JobService

    data = request.json
    job_id = data.get("job_id")

    if not job_id:
        return jsonify({"status": "error", "message": "Missing job_id"}), 400

    try:
        success, msg = JobService.reject_job(job_id)
        if success:
            return jsonify({"status": "ok", "message": msg})
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        print(f"Reject Job Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/approve/shop", methods=["POST"])
def api_admin_approve_shop():
    """ショップリクエストを承認"""
    data = request.json
    print(f"[DEBUG] approve_shop received: {data}")
    request_id = data.get("request_id")

    if not request_id:
        print(f"[DEBUG] Missing request_id in data: {data}")
        return jsonify({"status": "error", "message": "Missing request_id"}), 400

    try:
        result = ShopService.approve_request(request_id)
        print(f"[DEBUG] approve_request result: {result}")
        if result:
            return jsonify({"status": "ok"})
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to approve - request not found or already processed",
                }
            ), 500
    except Exception as e:
        print(f"Approve Shop Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/reject/shop", methods=["POST"])
def api_admin_reject_shop():
    """ショップリクエストを却下（返金）"""
    data = request.json
    print(f"[DEBUG] reject_shop received: {data}")
    request_id = data.get("request_id")
    user_id = data.get("user_id")
    cost = data.get("cost", 0)

    if not request_id:
        print(f"[DEBUG] Missing request_id in data: {data}")
        return jsonify({"status": "error", "message": "Missing request_id"}), 400

    try:
        result = ShopService.deny_request(request_id)
        print(f"[DEBUG] deny_request result: {result}")
        if result:
            # 返金処理
            if user_id and cost:
                EconomyService.add_exp(user_id, int(cost), f"REFUND_{request_id}")
            return jsonify({"status": "ok"})
        else:
            return jsonify(
                {
                    "status": "error",
                    "message": "Failed to reject - request not found or already processed",
                }
            ), 500
    except Exception as e:
        print(f"Reject Shop Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/approve/mission", methods=["POST"])
def api_admin_approve_mission():
    """ミッション完了を承認"""
    from services.mission import MissionService

    data = request.json
    mission_id = data.get("mission_id")

    if not mission_id:
        return jsonify({"status": "error", "message": "Missing mission_id"}), 400

    try:
        success, msg = MissionService.approve_mission(mission_id)
        if success:
            return jsonify({"status": "ok", "message": msg})
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        print(f"Approve Mission Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@web_bp.route("/api/admin/reject/mission", methods=["POST"])
def api_admin_reject_mission():
    """ミッション完了を却下"""
    from services.mission import MissionService

    data = request.json
    mission_id = data.get("mission_id")

    if not mission_id:
        return jsonify({"status": "error", "message": "Missing mission_id"}), 400

    try:
        success, msg = MissionService.reject_mission(mission_id)
        if success:
            return jsonify({"status": "ok", "message": msg})
        else:
            return jsonify({"status": "error", "message": msg}), 500
    except Exception as e:
        print(f"Reject Mission Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# --- Static and Legacy ---
