from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SettingsBase(BaseModel):
    email_notifications: bool = True
    low_stock_alerts: bool = True
    auto_confirmations: bool = False

class SettingsUpdate(SettingsBase):
    pass

class SettingsResponse(SettingsBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
