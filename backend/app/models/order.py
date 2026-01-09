from sqlalchemy import Column, BigInteger, String, DECIMAL, Enum, Text, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class OrderStatus(str, enum.Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    WAITING_CONTACT = "WAITING_CONTACT"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"


class Order(Base):
    __tablename__ = "orders"

    id = Column(BIGINT(unsigned=True), primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Datos de envío
    shipping_full_name = Column(String(255), nullable=False)
    shipping_phone = Column(String(20), nullable=False)
    shipping_address = Column(String(500), nullable=False)
    shipping_district = Column(String(100), nullable=False)
    shipping_city = Column(String(100), nullable=False)
    shipping_reference = Column(String(255), nullable=True)
    
    # Montos
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    tax = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    shipping_cost = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    total = Column(DECIMAL(10, 2), nullable=False)
    
    # Estado
    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING_PAYMENT,
        index=True
    )
    notes = Column(Text, nullable=True)
    
    # Fechas
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BIGINT(unsigned=True), primary_key=True, index=True, autoincrement=True)
    order_id = Column(BIGINT(unsigned=True), ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(BIGINT(unsigned=True), ForeignKey("products.id"), nullable=False, index=True)
    
    # Snapshot del producto al momento de la compra
    product_name = Column(String(255), nullable=False)
    product_price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    
    # Fechas
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
