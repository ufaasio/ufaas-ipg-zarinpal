from datetime import datetime

from fastapi_mongo_base.models import BusinessEntity

from .config import ZarinpalConfig
from .schemas import PurchaseSchema


class Purchase(PurchaseSchema, BusinessEntity):
    callback_url: str

    class Settings:
        indexes = BusinessEntity.Settings.indexes

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
