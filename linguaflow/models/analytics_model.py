from models.user_model import UserModel
from models.translation_model import TranslationModel


class AnalyticsModel:
    @staticmethod
    def get_dashboard_stats() -> dict:
        return {
            "total_users": UserModel.count(),
            "new_users_this_week": UserModel.count_recent(days=7),
            "daily_translations": TranslationModel.count_today(),
            "avg_response_time": TranslationModel.avg_response_time_today(),
            "failed_translations": TranslationModel.failed_count_today(),
        }

    @staticmethod
    def get_volume_chart(days=14) -> list:
        return TranslationModel.volume_last_n_days(days)

    @staticmethod
    def get_top_pairs(limit=5) -> list:
        raw = TranslationModel.top_language_pairs(limit)
        return [
            {"pair": f"{r['_id']['source']} → {r['_id']['target']}", "count": r["count"]}
            for r in raw
        ]
