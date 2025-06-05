import base64
import hashlib
import hmac
import os
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

import httpx
from pydantic import BaseModel, Field

from utils import send_to_bark


class SnapshotConfig(BaseModel):
    """Configuration model for Aliyun Snapshot operations"""

    disk_id: str = Field(..., description="ID of the disk to snapshot")
    snapshot_name: str = Field(
        default_factory=lambda: f"Auto-Backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    )
    access_key_id: str = Field(..., description="Aliyun Access Key ID")
    access_key_secret: str = Field(..., description="Aliyun Access Key Secret")
    region_id: str = Field(default="ap-southeast-1")


def generate_signature(params, secret):
    """Generate Aliyun API signature"""
    sorted_params = sorted(params.items())
    query_string = urlencode(sorted_params, safe="")
    sign_str = f"GET&%2F&{quote(query_string)}"
    return base64.b64encode(
        hmac.new(f"{secret}&".encode(), sign_str.encode(), hashlib.sha1).digest()
    ).decode()


async def aliyun_request(action, config, extra_params=None):
    """Make a generic Aliyun API request with proper authentication"""
    params = {
        "Action": action,
        "Version": "2020-06-01",
        "Format": "JSON",
        "RegionId": config.region_id,
        "DiskId": config.disk_id,
        "AccessKeyId": config.access_key_id,
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": uuid.uuid4().hex,
        "Timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    if extra_params:
        params.update(extra_params)

    params["Signature"] = generate_signature(params, config.access_key_secret)
    url = f"https://swas.{config.region_id}.aliyuncs.com/?{urlencode(params)}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()


async def get_aliyun_config():
    return SnapshotConfig(
        disk_id=os.getenv("ALIYUN_DISK_ID"),
        access_key_id=os.getenv("ALIYUN_ACCESS_KEY_ID"),
        access_key_secret=os.getenv("ALIYUN_ACCESS_KEY_SECRET"),
        region_id=os.getenv("ALIYUN_REGION_ID", "ap-southeast-1"),
    )


async def list_snapshots():
    config = await get_aliyun_config()
    return await aliyun_request("ListSnapshots", config)


async def create_snapshot():
    config = await get_aliyun_config()
    data = await list_snapshots()
    try:
        snapshots = data.get("Snapshots", [])
        if len(snapshots) >= 3:
            oldest_snapshot = min(snapshots, key=lambda x: x.get("CreationTime", ""))
            delete_msg = await aliyun_request(
                "DeleteSnapshot",
                config,
                {"SnapshotId": oldest_snapshot.get("SnapshotId")},
            )
            create_msg = await aliyun_request(
                "CreateSnapshot", config, {"SnapshotName": config.snapshot_name}
            )
    except Exception as e:
        bark_msg = await send_to_bark(
            content=f"异常报错: {e}",
        )
    finally:
        bark_msg = await send_to_bark(
            content=f"{config.snapshot_name}创建成功",
        )
    return {
        "delete_msg": delete_msg,
        "create_msg": create_msg,
        "bark_msg": bark_msg,
    }
