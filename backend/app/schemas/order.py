"""Pydantic schemas for orders."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime


class OrderItemSchema(BaseModel):
    product_id: str
    product_name: str
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    category: Optional[str] = None
    hs_code: Optional[str] = None  # Harmonized System code for export controls


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=255)
    customer_country: str = Field(min_length=2, max_length=100)
    customer_email: EmailStr
    items: List[OrderItemSchema] = Field(min_length=1)
    total_amount: float = Field(ge=0)
    currency: str = Field(default="USD", max_length=10)


class OrderResponse(BaseModel):
    id: str
    order_number: str
    customer_name: str
    customer_country: str
    customer_email: str
    items: List[Any]
    total_amount: float
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    total: int
    orders: List[OrderResponse]
