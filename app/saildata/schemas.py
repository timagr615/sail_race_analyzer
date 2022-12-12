from datetime import datetime
from enum import Enum
from pydantic import BaseModel, FilePath


class SailDataBase(BaseModel):
    sail_boat: str | None
    wind_speed: str | None
    description: str | None
    notes: str | None


class SailDataUpload(SailDataBase):
    file_path: str
    file_size: int
    user_id: int


class SailDataDB(SailDataUpload):
    id: int
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

    class Config:
        orm_mode = True


class SailDataUpdate(SailDataBase):
    id: int
