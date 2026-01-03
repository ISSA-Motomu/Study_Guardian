import math


class SagaStats:
    POPULATION_J1 = 7676
    MEAN_J1 = 60
    STD_J1 = 45
    SAGANISHI_LIMIT = 240

    @staticmethod
    def get_school_level(deviation):
        """偏差値から相当する高校レベルを判定（佐賀県モデル）"""
        if deviation >= 68:
            return "佐賀西高校"
        if deviation >= 60:
            return "致遠館高校"
        if deviation >= 55:
            return "佐賀北高校"
        if deviation >= 50:
            return "佐賀東高校"
        if deviation >= 45:
            return "佐賀商業高校"
        if deviation >= 40:
            return "佐賀工業高校"
        if deviation >= 38:
            return "佐賀北稜高校"
        return "基礎固めが必要"

    @staticmethod
    def calculate(study_minutes):
        """1日の学習時間から偏差値を計算"""
        return SagaStats._calculate_generic(study_minutes, days=1)

    @staticmethod
    def calculate_weekly(study_minutes):
        """1週間の学習時間から偏差値を計算"""
        return SagaStats._calculate_generic(study_minutes, days=7)

    @staticmethod
    def calculate_monthly(study_minutes):
        """1ヶ月の学習時間から偏差値を計算"""
        return SagaStats._calculate_generic(study_minutes, days=30)

    @staticmethod
    def _calculate_generic(study_minutes, days=1):
        if study_minutes <= 0:
            return None

        # 期間に応じた平均と標準偏差を推定
        # 平均は日数倍、標準偏差は√日数倍（独立試行を仮定）
        mean = SagaStats.MEAN_J1 * days
        std = SagaStats.STD_J1 * math.sqrt(days)

        z_score = (study_minutes - mean) / std
        deviation = z_score * 10 + 50

        # 上位%計算
        p_value = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
        top_percent = 1 - p_value

        rank = int(SagaStats.POPULATION_J1 * top_percent)
        if rank < 1:
            rank = 1

        # ごぼう抜き計算 (0分だった場合の順位との差)
        zero_z = (0 - mean) / std
        zero_p = 0.5 * (1 + math.erf(zero_z / math.sqrt(2)))
        zero_rank = int(SagaStats.POPULATION_J1 * (1 - zero_p))
        overtaken = zero_rank - rank

        return {
            "rank": rank,
            "deviation": round(deviation, 1),
            "school_level": SagaStats.get_school_level(deviation),
            "overtaken": overtaken,
            "is_saganishi": rank <= SagaStats.SAGANISHI_LIMIT,
        }
