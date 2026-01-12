from sqlalchemy import Column, Integer, Boolean, DateTime, Numeric, String
from sqlalchemy.sql import func
from app.database import Base

class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    email_notifications = Column(Boolean, default=True)
    low_stock_alerts = Column(Boolean, default=True)
    auto_confirmations = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    
    # New fields
    shipping_base_cost = Column(Numeric(10, 2), default=0.0)
    free_shipping_threshold = Column(Numeric(10, 2), default=0.0)
    business_hours = Column(String, nullable=True)
    social_facebook = Column(String, nullable=True)
    social_instagram = Column(String, nullable=True)
    social_tiktok = Column(String, nullable=True)
