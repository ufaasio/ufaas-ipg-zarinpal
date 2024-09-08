from datetime import datetime
from decimal import Decimal
from typing import Literal

from apps.base.schemas import BusinessOwnedEntitySchema
from pydantic import BaseModel, field_validator
from utils import numtools


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

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return numtools.decimal_amount(value)


class PurchaseCreateSchema(BaseModel):
    amount: Decimal
    description: str
    phone: str | None = None
    is_test: bool = False

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return numtools.decimal_amount(value)
