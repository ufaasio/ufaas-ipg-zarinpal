import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Literal

from fastapi_mongo_base.schemas import BusinessEntitySchema
from fastapi_mongo_base.utils import bsontools, texttools
from pydantic import BaseModel, field_serializer, field_validator


class PurchaseStatus(str, Enum):
    INIT = "INIT"
    PENDING = "PENDING"
    FAILED = "FAILED"
    SUCCESS = "SUCCESS"
    REFUNDED = "REFUNDED"


class PurchaseSchema(BusinessEntitySchema):
    user_id: uuid.UUID | None
    wallet_id: uuid.UUID
    amount: Decimal

    phone: str | None = None
    description: str  # | None = None

    is_test: bool = False
    status: PurchaseStatus = PurchaseStatus.INIT

    authority: str | None = None

    failure_reason: str | None = None
    verified_at: datetime | None = None
    ref_id: int | None = None

    @field_serializer("status")
    def serialize_status(self, value: PurchaseStatus):
        return value.value

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return bsontools.decimal_amount(value)


class PurchaseCreateSchema(BaseModel):
    wallet_id: uuid.UUID
    amount: Decimal
    description: str
    callback_url: str
    phone: str | None = None
    is_test: bool = False

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return bsontools.decimal_amount(value)

    @field_validator("callback_url", mode="before")
    def validate_callback_url(cls, value):
        if not texttools.is_valid_url(value):
            raise ValueError(f"Invalid URL {value}")
        return value


class Participant(BaseModel):
    wallet_id: uuid.UUID
    amount: Decimal


class ProposalCreateSchema(BaseModel):
    amount: Decimal
    description: str | None = None
    note: str | None = None
    currency: str
    task_status: Literal["draft", "init"] = "draft"
    participants: list[Participant]
    meta_data: dict[str, Any] | None = None
