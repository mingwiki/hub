import base64
import hashlib
import hmac
import uuid
from datetime import datetime, timezone
from urllib.parse import quote, urlencode

import httpx
from fastapi import APIRouter, Header
from pydantic import BaseModel, Field

from models import get_config
from utils import is_authorized, send_to_bark

router = APIRouter(prefix="/aliyun", tags=["Aliyun API"])


class SnapshotConfig(BaseModel):
    """Configuration model for Aliyun Snapshot operations"""

    disk_id: str = Field(..., description="ID of the disk to snapshot")
    snapshot_name: str = Field(default_factory=lambda: f"Auto-Backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    access_key_id: str = Field(..., description="Aliyun Access Key ID")
    access_key_secret: str = Field(..., description="Aliyun Access Key Secret")
    region_id: str = Field(default="ap-southeast-1")


def generate_signature(params, secret):
    """Generate Aliyun API signature"""
    sorted_params = sorted(params.items())
    query_string = urlencode(sorted_params, safe="")
    sign_str = f"GET&%2F&{quote(query_string)}"
    return base64.b64encode(hmac.new(f"{secret}&".encode(), sign_str.encode(), hashlib.sha1).digest()).decode()


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
    keys = await get_config("aliyun_accesskey")
    return SnapshotConfig(
        disk_id=keys["disk_id"],
        access_key_id=keys["access_key_id"],
        access_key_secret=keys["access_key_secret"],
        region_id=keys.get("region_id", "ap-southeast-1"),
    )


async def list_snapshots():
    config = await get_aliyun_config()
    return await aliyun_request("ListSnapshots", config)


async def create_snapshot():
    config = await get_aliyun_config()
    data = await list_snapshots()
    snapshots = data.get("Snapshots", [])

    if len(snapshots) >= 3:
        oldest_snapshot = min(snapshots, key=lambda x: x.get("CreationTime", ""))
        await aliyun_request("DeleteSnapshot", config, {"SnapshotId": oldest_snapshot.get("SnapshotId")})
    bark = await get_config("bark")
    return {
        "snapshot": await aliyun_request("CreateSnapshot", config, {"SnapshotName": config.snapshot_name}),
        "notification": await send_to_bark(
            token=bark["fuming"],
            title="服务器快照",
            content=f"{config.snapshot_name} 创建成功",
            group="Snapshot",
        ),
    }


@router.post("/snapshot")
@is_authorized
async def backup_snapshot(x_token=Header(default=None)):
    """Create a snapshot for an Aliyun Lightweight Server"""
    return await create_snapshot()


@router.get("/snapshot")
@is_authorized
async def get_snapshot(x_token=Header(default=None)):
    """Get snapshots info for an Aliyun Lightweight Server"""
    return await list_snapshots()
