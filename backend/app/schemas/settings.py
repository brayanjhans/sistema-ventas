from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SettingsBase(BaseModel):
    email_notifications: bool = True
    low_stock_alerts: bool = True
    auto_confirmations: bool = False
    
    # New fields
    shipping_base_cost: float = 0.0
    free_shipping_threshold: float = 0.0
    business_hours: Optional[str] = None
    social_facebook: Optional[str] = None
    social_instagram: Optional[str] = None
    social_tiktok: Optional[str] = None

class SettingsUpdate(SettingsBase):
    pass

class SettingsResponse(SettingsBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True
