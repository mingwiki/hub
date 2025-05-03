from datetime import datetime, timezone

from database import Q, t_keyring


class Keyring:
    def set(key: str, data: dict):

        return t_keyring.upsert(
            {
                "key": key,
                "val": data,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            Q.key == key,
        )

    def get(key: str):
        entry = t_keyring.get(Q.key == key)

        return entry["val"] if entry else None

    def delete(key: str):
        return t_keyring.remove(Q.key == key)
