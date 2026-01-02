import time


class Debouncer:
    _cache = {}
    _ttl = 5.0  # 5秒間は同じ操作を無視

    @classmethod
    def is_locked(cls, user_id, action_key):
        """
        指定されたユーザーとアクションの組み合わせがロックされているか確認。
        ロックされていなければロックしてFalseを返す。
        ロックされていればTrueを返す。
        """
        now = time.time()
        key = f"{user_id}:{action_key}"

        # 期限切れのエントリを削除（簡易的なGC）
        # 毎回全走査は重いので、対象キーだけチェックし、
        # たまに全体を掃除するロジックが良いが、
        # ここではシンプルに対象キーのTTLチェックのみ行う。

        last_time = cls._cache.get(key)

        if last_time:
            if now - last_time < cls._ttl:
                return True  # ロック中

        # 新しいタイムスタンプで更新
        cls._cache[key] = now
        return False
