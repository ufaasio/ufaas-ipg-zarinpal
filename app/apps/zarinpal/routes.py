import logging
import uuid
from decimal import Decimal

from fastapi import Request
from fastapi.responses import RedirectResponse
from ufaas_fastapi_business.middlewares import get_business
from ufaas_fastapi_business.routes import AbstractAuthRouter
from usso import Usso

from .models import Purchase
from .schemas import PurchaseCreateSchema, PurchaseSchema, PurchaseStatus
from .services import create_proposal, start_purchase, verify_purchase


class PurchaseRouter(AbstractAuthRouter[Purchase, PurchaseSchema]):
    def __init__(self):
        super().__init__(model=Purchase, schema=PurchaseSchema, user_dependency=None)

    def config_schemas(self, schema, **kwargs):
        super().config_schemas(schema)
        self.create_request_schema = PurchaseCreateSchema

    def config_routes(self):
        self.router.add_api_route(
            "/",
            self.list_items,
            methods=["GET"],
            response_model=self.list_response_schema,
            status_code=200,
        )
        self.router.add_api_route(
            "/{uid:uuid}",
            self.retrieve_item,
            methods=["GET"],
            response_model=self.retrieve_response_schema,
            status_code=200,
        )
        self.router.add_api_route(
            "/",
            self.create_item,
            methods=["POST"],
            response_model=self.create_response_schema,
            status_code=201,
        )
        self.router.add_api_route(
            "/start",
            self.start_direct_purchase,
            methods=["GET"],
            # response_model=self.retrieve_response_schema,
        )
        self.router.add_api_route(
            "/{uid:uuid}/start",
            self.start_purchase,
            methods=["GET"],
            # response_model=self.retrieve_response_schema,
        )
        self.router.add_api_route(
            "/{uid:uuid}/verify",
            self.verify_purchase,
            methods=["GET"],
            # response_model=self.retrieve_response_schema,
        )

    async def retrieve_item(self, request: Request, uid: uuid.UUID):
        return await super().retrieve_item(request, uid)

    async def create_item(self, request: Request, item: PurchaseCreateSchema):

        business = await get_business(request)

        try:
            user = await Usso(
                jwt_config=business.config.jwt_config
            ).jwt_access_security(request)
        except Exception as e:
            user = None
            logging.warning(f"create item not user: {e}")

        user_id = user.uid if user else business.user_id

        item = self.model(
            business_name=business.name,
            user_id=user_id,
            **item.model_dump(),
        )
        await item.save()
        return self.create_response_schema(**item.model_dump())

        # return await super().create_item(request, item.model_dump())

    async def start_direct_purchase(
        self,
        request: Request,
        wallet_id: uuid.UUID,
        amount: Decimal,
        description: str,
        callback_url: str,
        test: bool = False,
    ):
        purchase: Purchase = await self.create_item(
            request,
            PurchaseCreateSchema(
                wallet_id=wallet_id,
                amount=amount,
                description=description,
                callback_url=callback_url,
                is_test=test,
            ),
        )
        logging.info(
            f"start_direct_purchase: {wallet_id=}, {amount=}, {description=}, {callback_url=}, {test=}"
        )
        return await self.start_purchase(request, purchase.uid)

    async def start_purchase(self, request: Request, uid: uuid.UUID):
        business = await get_business(request)

        item: Purchase = await self.get_item(uid, business_name=business.name)
        start_data = await start_purchase(business=business, purchase=item)
        if start_data["status"]:
            return RedirectResponse(url=item.start_payment_url)

    async def verify_purchase(
        self, request: Request, uid: uuid.UUID, Status: str, Authority: str
    ):
        try:
            business = await get_business(request)

            item: Purchase = await self.get_item(uid, business_name=business.name)
            if item.status != PurchaseStatus.PENDING:
                return RedirectResponse(url=item.callback_url)

            purchase = await verify_purchase(
                business=business, item=item, status=Status, authority=Authority
            )

            if purchase.status == PurchaseStatus.SUCCESS:
                await create_proposal(purchase, business)

            return RedirectResponse(
                url=f"{purchase.callback_url}?success={purchase.is_successful}"
            )
        except Exception as e:
            logging.error(f"verify error: {e}")
            raise e


router = PurchaseRouter().router
