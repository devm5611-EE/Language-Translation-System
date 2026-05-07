import datetime
from bson import ObjectId
from database.mongodb import get_db


class TranslationModel:
    COL = "translations"

    @staticmethod
    def col():
        return get_db()[TranslationModel.COL]

    @staticmethod
    def create(user_id, source_text, translated_text, source_lang,
               target_lang, confidence, model_used, response_time_ms) -> str:
        doc = {
            "user_id": str(user_id),
            "source_text": source_text,
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "confidence": round(float(confidence), 4),
            "model_used": model_used,
            "response_time_ms": int(response_time_ms),
            "char_count": len(source_text),
            "created_at": datetime.datetime.utcnow(),
        }
        r = TranslationModel.col().insert_one(doc)
        return str(r.inserted_id)

    @staticmethod
    def find_by_user(user_id, skip=0, limit=20, source_lang=None,
                     target_lang=None, search=None, sort="newest"):
        import re
        query = {"user_id": str(user_id)}
        if source_lang:
            query["source_lang"] = source_lang
        if target_lang:
            query["target_lang"] = target_lang
        if search:
            # Escape special regex characters to prevent NoSQL injection
            escaped_search = re.escape(search.strip())
            query["$or"] = [
                {"source_text": {"$regex": escaped_search, "$options": "i"}},
                {"translated_text": {"$regex": escaped_search, "$options": "i"}},
            ]
        sort_dir = -1 if sort == "newest" else 1
        return list(TranslationModel.col().find(query).sort("created_at", sort_dir).skip(skip).limit(limit))

    @staticmethod
    def count_by_user(user_id) -> int:
        return TranslationModel.col().count_documents({"user_id": str(user_id)})

    @staticmethod
    def delete_one(translation_id, user_id) -> bool:
        try:
            r = TranslationModel.col().delete_one({"_id": ObjectId(translation_id), "user_id": str(user_id)})
            return r.deleted_count > 0
        except Exception:
            return False

    @staticmethod
    def delete_all_by_user(user_id) -> int:
        r = TranslationModel.col().delete_many({"user_id": str(user_id)})
        return r.deleted_count

    @staticmethod
    def count_today() -> int:
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return TranslationModel.col().count_documents({"created_at": {"$gte": today}})

    @staticmethod
    def avg_response_time_today() -> float:
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"created_at": {"$gte": today}}},
            {"$group": {"_id": None, "avg": {"$avg": "$response_time_ms"}}},
        ]
        result = list(TranslationModel.col().aggregate(pipeline))
        return round(result[0]["avg"] / 1000, 2) if result else 0.0

    @staticmethod
    def failed_count_today() -> int:
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return TranslationModel.col().count_documents({"created_at": {"$gte": today}, "confidence": {"$lt": 0.5}})

    @staticmethod
    def volume_last_n_days(n=14) -> list:
        since = datetime.datetime.utcnow() - datetime.timedelta(days=n)
        pipeline = [
            {"$match": {"created_at": {"$gte": since}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}, "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        return list(TranslationModel.col().aggregate(pipeline))

    @staticmethod
    def top_language_pairs(limit=5) -> list:
        pipeline = [
            {"$group": {"_id": {"source": "$source_lang", "target": "$target_lang"}, "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]
        return list(TranslationModel.col().aggregate(pipeline))

    @staticmethod
    def user_stats_today(user_id) -> dict:
        today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        pipeline = [
            {"$match": {"user_id": str(user_id), "created_at": {"$gte": today}}},
            {"$group": {
                "_id": None,
                "count": {"$sum": 1},
                "avg_confidence": {"$avg": "$confidence"},
                "last_response_time": {"$last": "$response_time_ms"},
                "total_chars": {"$sum": "$char_count"},
            }},
        ]
        result = list(TranslationModel.col().aggregate(pipeline))
        if result:
            r = result[0]
            return {
                "count": r.get("count", 0),
                "avg_confidence": round((r.get("avg_confidence") or 0) * 100, 1),
                "last_response_time": f"{(r.get('last_response_time') or 0) / 1000:.1f}s",
                "total_chars": r.get("total_chars", 0),
            }
        return {"count": 0, "avg_confidence": 0, "last_response_time": "—", "total_chars": 0}

    @staticmethod
    def to_dict(t: dict) -> dict:
        return {
            "id": str(t["_id"]),
            "source_text": t.get("source_text", ""),
            "translated_text": t.get("translated_text", ""),
            "source_lang": t.get("source_lang", ""),
            "target_lang": t.get("target_lang", ""),
            "confidence": t.get("confidence", 0),
            "model_used": t.get("model_used", ""),
            "response_time_ms": t.get("response_time_ms", 0),
            "char_count": t.get("char_count", 0),
            "created_at": t["created_at"].isoformat() if isinstance(t.get("created_at"), datetime.datetime) else "",
        }
