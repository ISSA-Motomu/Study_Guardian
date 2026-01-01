import math

class SagaStats:
    POPULATION_J1 = 7676
    MEAN_J1 = 60
    STD_J1 = 45
    SAGANISHI_LIMIT = 240

    @staticmethod
    def calculate(study_minutes):
        if study_minutes <= 0: return None
        
        z_score = (study_minutes - SagaStats.MEAN_J1) / SagaStats.STD_J1
        deviation = z_score * 10 + 50
        
        # 上位%計算
        p_value = 0.5 * (1 + math.erf(z_score / math.sqrt(2)))
        top_percent = (1 - p_value)
        
        rank = int(SagaStats.POPULATION_J1 * top_percent)
        if rank < 1: rank = 1
        
        # ごぼう抜き計算
        zero_z = (0 - SagaStats.MEAN_J1) / SagaStats.STD_J1
        zero_p = 0.5 * (1 + math.erf(zero_z / math.sqrt(2)))
        zero_rank = int(SagaStats.POPULATION_J1 * (1 - zero_p))
        overtaken = zero_rank - rank

        return {
            "rank": rank,
            "deviation": round(deviation, 1),
            "overtaken": overtaken,
            "is_saganishi": rank <= SagaStats.SAGANISHI_LIMIT
        }