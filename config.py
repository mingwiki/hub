from fastapi import HTTPException

from models.db import KeysDB
from utils import logger

log = logger(__name__)


class Config:
    _configs = {
        "gitea_oauth": None,
        "cloudflare_ddns": None,
        "miniflux": None,
        "bark": None,
        "aliyun_accesskey": None,
    }

    @classmethod
    async def _load_and_validate_config(
        cls, name: str, required_keys: list[str] = None
    ):
        if cls._configs.get(name) is None:
            config = await KeysDB.get(name)
            log.info(f"Loading {name} config: {config}")

            if not config:
                raise HTTPException(
                    status_code=500, detail=f"{name.title()} config not found"
                )

            cls._configs[name] = config

            # Validate required keys
            if required_keys:
                missing_keys = [key for key in required_keys if key not in config]
                if missing_keys:
                    log.error(f"Missing keys in {name} config: {missing_keys}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Missing keys in {name} config: {missing_keys}",
                    )

        return cls._configs[name]

    @classmethod
    async def get_gitea_oauth(cls):
        return await cls._load_and_validate_config(
            "gitea_oauth",
            ["authorize_url", "token_url", "user_url", "client_id", "client_secret"],
        )

    @classmethod
    async def get_github_oauth(cls):
        return await cls._load_and_validate_config(
            "github_oauth",
            ["authorize_url", "token_url", "user_url", "client_id", "client_secret"],
        )

    @classmethod
    async def get_cloudflare_ddns(cls):
        return await cls._load_and_validate_config("cloudflare_ddns")

    @classmethod
    async def get_aliyun_accesskey(cls):
        return await cls._load_and_validate_config(
            "aliyun_accesskey",
            ["access_key_id", "access_key_secret", "region_id", "disk_id"],
        )

    @classmethod
    async def get_miniflux(cls):
        return await cls._load_and_validate_config("miniflux")

    @classmethod
    async def get_bark(cls):
        return await cls._load_and_validate_config("bark")

    @classmethod
    async def reset_cache(cls):
        cls._configs.clear()
