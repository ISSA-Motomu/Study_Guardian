import time
from functools import wraps


class SimpleCache:
    def __init__(self, ttl=300):
        self.ttl = ttl
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            val, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return val
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        self.cache[key] = (value, time.time())

    def clear(self):
        self.cache = {}

    def invalidate(self, key):
        """特定のキーのキャッシュを無効化"""
        if key in self.cache:
            del self.cache[key]


# グローバルキャッシュインスタンス
# 商品リストはあまり変わらないので長め (5分)
shop_items_cache = SimpleCache(ttl=300)

# ジョブリストはステータスが変わるので短め (1分)
job_list_cache = SimpleCache(ttl=60)

# ユーザーの状態管理 (5分)
user_state_cache = SimpleCache(ttl=300)

# ===== 新規キャッシュ（API 429対策）=====
# 週間ランキング (2分)
ranking_cache = SimpleCache(ttl=120)

# ユーザー統計 (2分)
user_stats_cache = SimpleCache(ttl=120)

# 最近のアクティビティ (1分)
activity_cache = SimpleCache(ttl=60)

# 承認待ちリスト (30秒)
pending_cache = SimpleCache(ttl=30)

# 全レコードキャッシュ (シート単位、30秒)
sheet_data_cache = SimpleCache(ttl=30)

# 目標データ (2分)
goals_cache = SimpleCache(ttl=120)


def cached(cache_instance, key_func=None):
    """
    関数の結果をキャッシュするデコレータ
    :param cache_instance: SimpleCacheのインスタンス
    :param key_func: 引数からキャッシュキーを生成する関数 (省略時は引数なしとみなす)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # 引数がない場合は関数名を含めてユニークにする
                key = f"{func.__module__}.{func.__name__}"

            cached_val = cache_instance.get(key)
            if cached_val is not None:
                # print(f"Cache Hit: {func.__name__} key={key}")
                return cached_val

            # print(f"Cache Miss: {func.__name__} key={key}")
            result = func(*args, **kwargs)
            cache_instance.set(key, result)
            return result

        return wrapper

    return decorator


def invalidate_all_caches():
    """全キャッシュをクリア"""
    shop_items_cache.clear()
    job_list_cache.clear()
    user_state_cache.clear()
    ranking_cache.clear()
    user_stats_cache.clear()
    activity_cache.clear()
    pending_cache.clear()
    sheet_data_cache.clear()
    goals_cache.clear()
