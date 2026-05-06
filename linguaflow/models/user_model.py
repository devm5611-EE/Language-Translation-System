import datetime
from bson import ObjectId
from database.mongodb import get_db


class UserModel:
    COL = "users"

    @staticmethod
    def col():
        return get_db()[UserModel.COL]

    @staticmethod
    def create(name: str, email: str, hashed_pw: str, role: str = "user") -> str:
        doc = {
            "name": name.strip(),
            "email": email.lower().strip(),
            "password": hashed_pw,
            "role": role,
            "preferences": {
                "dark_mode": False,
                "auto_detect": True,
                "save_history": True,
                "email_notifications": True,
            },
            "is_active": True,
            "translation_count": 0,
            "created_at": datetime.datetime.utcnow(),
            "updated_at": datetime.datetime.utcnow(),
        }
        result = UserModel.col().insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def find_by_email(email: str):
        return UserModel.col().find_one({"email": email.lower().strip()})

    @staticmethod
    def find_by_id(user_id: str):
        try:
            return UserModel.col().find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    @staticmethod
    def update(user_id: str, updates: dict) -> bool:
        updates["updated_at"] = datetime.datetime.utcnow()
        r = UserModel.col().update_one({"_id": ObjectId(user_id)}, {"$set": updates})
        return r.modified_count > 0

    @staticmethod
    def increment_count(user_id: str):
        UserModel.col().update_one(
            {"_id": ObjectId(user_id)},
            {"$inc": {"translation_count": 1}, "$set": {"updated_at": datetime.datetime.utcnow()}}
        )

    @staticmethod
    def delete(user_id: str) -> bool:
        r = UserModel.col().delete_one({"_id": ObjectId(user_id)})
        return r.deleted_count > 0

    @staticmethod
    def get_all(skip=0, limit=50):
        return list(UserModel.col().find({}).skip(skip).limit(limit).sort("created_at", -1))

    @staticmethod
    def count() -> int:
        return UserModel.col().count_documents({})

    @staticmethod
    def count_recent(days=7) -> int:
        since = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        return UserModel.col().count_documents({"created_at": {"$gte": since}})

    @staticmethod
    def to_public(user: dict) -> dict:
        if not user:
            return {}
        return {
            "id": str(user["_id"]),
            "name": user.get("name", ""),
            "email": user.get("email", ""),
            "role": user.get("role", "user"),
            "preferences": user.get("preferences", {}),
            "translation_count": user.get("translation_count", 0),
            "is_active": user.get("is_active", True),
            "created_at": user["created_at"].isoformat() if isinstance(user.get("created_at"), datetime.datetime) else "",
        }
