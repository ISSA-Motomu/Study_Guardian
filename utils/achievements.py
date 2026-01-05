from enum import Enum
from typing import List, Dict, Optional
import datetime


class AchievementType(Enum):
    EARLY_BIRD = "early_bird"  # 朝活（8時前の勉強）
    STREAK_3 = "streak_3"  # 3日継続
    FIRST_STEP = "first_step"  # 初めての勉強
    NIGHT_OWL = "night_owl"  # 夜更かし（22時以降）
    LONG_SESSION = "long_session"  # 60分以上の勉強


class Achievement:
    def __init__(
        self, id: AchievementType, title: str, description: str, icon_url: str
    ):
        self.id = id
        self.title = title
        self.description = description
        self.icon_url = icon_url


# 実績の定義マスタ
# アイコンは仮のURLまたはLINEのEmoji/Stickerを使うが、ここでは画像URLを想定
# 実際の運用では静的ファイルとしてhostingするか、外部URLを使う
ACHIEVEMENT_MASTER = {
    AchievementType.EARLY_BIRD: Achievement(
        AchievementType.EARLY_BIRD,
        "早起き鳥",
        "朝8時前に勉強を開始した",
        "https://cdn-icons-png.flaticon.com/512/3075/3075908.png",
    ),
    AchievementType.STREAK_3: Achievement(
        AchievementType.STREAK_3,
        "三日坊主卒業",
        "3日連続で勉強した",
        "https://cdn-icons-png.flaticon.com/512/477/477406.png",
    ),
    AchievementType.FIRST_STEP: Achievement(
        AchievementType.FIRST_STEP,
        "はじめの一歩",
        "初めて勉強を記録した",
        "https://cdn-icons-png.flaticon.com/512/265/265674.png",
    ),
    AchievementType.NIGHT_OWL: Achievement(
        AchievementType.NIGHT_OWL,
        "夜更かし",
        "22時以降に勉強した",
        "https://cdn-icons-png.flaticon.com/512/547/547433.png",
    ),
    AchievementType.LONG_SESSION: Achievement(
        AchievementType.LONG_SESSION,
        "集中マスター",
        "1回で60分以上勉強した",
        "https://cdn-icons-png.flaticon.com/512/3557/3557635.png",
    ),
}


class AchievementManager:
    """実績の判定と表示コンポーネント生成を行うクラス"""

    @staticmethod
    def check_achievements(
        user_data: dict, current_session: dict
    ) -> List[AchievementType]:
        """
        勉強終了時などに呼び出し、新規獲得した実績のリストを返す。

        Args:
            user_data: ユーザーの全データ（過去の履歴含む）
            current_session: 今回の勉強セッション情報
                             {
                                 "start_time": "HH:MM:SS", (or datetime)
                                 "minutes": int,
                                 "is_first_ever": bool (optional)
                             }
        """
        newly_unlocked = []
        current_unlocked_str = str(user_data.get("unlocked_achievements", ""))
        # 既に獲得済みのセット
        unlocked_set = (
            set(current_unlocked_str.split(",")) if current_unlocked_str else set()
        )

        # --- 判定ロジック ---

        # 0. はじめの一歩
        # ユーザーデータのtotal_study_timeが今回分しかない、あるいは履歴が1件など
        # ここでは簡易的に current_session にフラグがあると仮定、もしくは user_data["total_study_time"] == minutes
        total_time = int(user_data.get("total_study_time", 0))
        minutes = current_session.get("minutes", 0)
        # 今回加算済みなら total_time == minutes (初回)
        # まだ加算前なら total_time == 0
        # 文脈によるが、finalize_study時点ではまだ加算されていないか、加算直後かによる。
        # 安全策として「今回が初回」判定は呼び出し元で行うか、履歴件数を見るのが確実。
        if current_session.get("is_first_ever", False):
            if AchievementType.FIRST_STEP.value not in unlocked_set:
                newly_unlocked.append(AchievementType.FIRST_STEP)

        # 1. 早起き判定 (開始時間が05:00-08:00)
        start_time_str = current_session.get("start_time")  # "HH:MM:SS"
        if start_time_str:
            try:
                # 時間のみの文字列 "HH:MM:SS" を想定
                st = datetime.datetime.strptime(start_time_str, "%H:%M:%S").time()
                if 5 <= st.hour < 8:
                    if AchievementType.EARLY_BIRD.value not in unlocked_set:
                        newly_unlocked.append(AchievementType.EARLY_BIRD)

                # 夜更かし (22:00以降)
                if st.hour >= 22 or st.hour < 3:
                    if AchievementType.NIGHT_OWL.value not in unlocked_set:
                        newly_unlocked.append(AchievementType.NIGHT_OWL)
            except ValueError:
                pass

        # 2. 長時間 (60分以上)
        if minutes >= 60:
            if AchievementType.LONG_SESSION.value not in unlocked_set:
                newly_unlocked.append(AchievementType.LONG_SESSION)

        # 3. 継続判定 (STREAK_3)
        # これは履歴データが必要。呼び出し元で判定してフラグを渡すか、HistoryServiceを使う必要がある。
        # ここでは current_session に "streak_days" があると仮定
        streak_days = current_session.get("streak_days", 0)
        if streak_days >= 3:
            if AchievementType.STREAK_3.value not in unlocked_set:
                newly_unlocked.append(AchievementType.STREAK_3)

        return newly_unlocked

    @staticmethod
    def generate_flex_component(unlocked_ids_str: str) -> dict:
        """
        ステータス画面（Flex Message）に埋め込むための実績グリッドを生成する。
        """
        unlocked_set = (
            set(str(unlocked_ids_str).split(",")) if unlocked_ids_str else set()
        )

        contents = []
        # 定義順にループして表示
        for ach_enum, ach_obj in ACHIEVEMENT_MASTER.items():
            is_unlocked = ach_enum.value in unlocked_set

            # アンロック時はカラー、未獲得時はグレーアウト(不透明度を下げる)
            opacity = "1.0" if is_unlocked else "0.3"
            # 未獲得時はモノクロフィルタっぽくしたいがFlexでは難しいので、
            # 画像自体を切り替えるか、opacityで表現。
            # ここではopacityとテキスト色で表現。

            color = "#000000" if is_unlocked else "#aaaaaa"

            # アイコンとテキストのコンポーネント
            tile = {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": ach_obj.icon_url,
                        "size": "xs",
                        "aspectMode": "fit",
                        "action": {
                            "type": "message",
                            "label": "detail",
                            "text": f"実績確認: {ach_obj.title}\n{ach_obj.description}",
                        },
                    },
                    {
                        "type": "text",
                        "text": ach_obj.title,
                        "size": "xxs",
                        "color": color,
                        "align": "center",
                        "wrap": True,
                        "margin": "xs",
                    },
                ],
                "width": "32%",  # 3列グリッド
                "paddingAll": "xs",
                "opacity": opacity,
                "backgroundColor": "#ffffff" if is_unlocked else "#f0f0f0",
                "cornerRadius": "md",
                "margin": "xs",
            }
            contents.append(tile)

        # Flex Messageのbox構造
        return {
            "type": "box",
            "layout": "horizontal",
            "wrap": True,
            "contents": contents,
            "margin": "md",
        }
