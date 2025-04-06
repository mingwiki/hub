from datetime import datetime

from pydantic import BaseModel, Field


class SnapshotConfig(BaseModel):
    """Configuration model for Aliyun Snapshot operations"""

    disk_id: str = Field(..., description="ID of the disk to snapshot")
    snapshot_name: str = Field(default_factory=lambda: f"Auto-Backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    access_key_id: str = Field(..., description="Aliyun Access Key ID")
    access_key_secret: str = Field(..., description="Aliyun Access Key Secret")
    region_id: str = Field(default="ap-southeast-1")


class User(BaseModel):
    id: int | None = None
    username: str
    password: str
    is_active: bool | None = None
    hashed_password: str | None = None
