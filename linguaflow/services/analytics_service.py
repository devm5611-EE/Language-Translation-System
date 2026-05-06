from models.analytics_model import AnalyticsModel
from models.user_model import UserModel


def get_admin_dashboard() -> dict:
    return {
        "stats": AnalyticsModel.get_dashboard_stats(),
        "volume_chart": AnalyticsModel.get_volume_chart(14),
        "top_pairs": AnalyticsModel.get_top_pairs(5),
    }


def get_all_users(page=1, per_page=20) -> dict:
    skip = (page - 1) * per_page
    users = UserModel.get_all(skip=skip, limit=per_page)
    total = UserModel.count()
    return {
        "users": [UserModel.to_public(u) for u in users],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }
