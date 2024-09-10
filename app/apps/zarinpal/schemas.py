from datetime import datetime
from decimal import Decimal
from typing import Literal

from apps.base.schemas import BusinessOwnedEntitySchema
from pydantic import BaseModel, field_validator
from utils import numtools, texttools


class PurchaseSchema(BusinessOwnedEntitySchema):
    amount: Decimal

    phone: str | None = None
    description: str | None = None

    is_test: bool = False
    status: Literal["INIT", "PENDING", "FAILED", "SUCCESS"] = "INIT"

    authority: str | None = None

    failure_reason: str | None = None
    verified_at: datetime | None = None
    ref_id: int | None = None

    @classmethod
    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return numtools.decimal_amount(value)


class PurchaseCreateSchema(BaseModel):
    amount: Decimal
    description: str
    callback_url: str
    phone: str | None = None
    is_test: bool = False

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return numtools.decimal_amount(value)

    @field_validator("callback_url", mode="before")
    def validate_callback_url(cls, value):
        if not texttools.is_valid_url(value):
            raise ValueError(f"Invalid URL {value}")
        return value
