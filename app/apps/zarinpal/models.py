from datetime import datetime
from decimal import Decimal
from typing import Literal

from apps.base.models import BusinessOwnedEntity
from pydantic import field_validator
from utils import numtools

from .config import ZarinpalConfig


class Purchase(BusinessOwnedEntity):
    amount: Decimal
    description: str
    callback_url: str

    phone: str | None = None

    is_test: bool = False
    status: Literal["INIT", "PENDING", "FAILED", "SUCCESS"] = "INIT"

    authority: str | None = None

    failure_reason: str | None = None
    verified_at: datetime | None = None
    ref_id: int | None = None

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):
        return numtools.decimal_amount(value)

    @classmethod
    async def get_purchase_by_authority(cls, business_name: str, authority: str):
        return await cls.find_one(
            cls.is_deleted == False,
            cls.business_name == business_name,
            cls.authority == authority,
        )

    async def success(self, ref_id: int):
        self.ref_id = ref_id
        self.status = "SUCCESS"
        self.verified_at = datetime.now()
        await self.save()

    async def fail(self, failure_reason: str = None):
        self.status = "FAILED"
        self.failure_reason = failure_reason
        await self.save()

    @property
    def config(self):
        return ZarinpalConfig(test=self.is_test)

    @property
    def is_successful(self):
        return self.status == "SUCCESS"

    @property
    def start_payment_url(self):
        return f"{self.config.start_payment_url}/{self.authority}"
