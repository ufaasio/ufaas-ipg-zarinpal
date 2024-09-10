import uuid
from decimal import Decimal

from apps.business.routes import AbstractAuthRouter
from fastapi import Request
from fastapi.responses import RedirectResponse

from .models import Purchase
from .schemas import PurchaseCreateSchema, PurchaseSchema
from .services import start_purchase, verify_purchase


class PurchaseRouter(AbstractAuthRouter[Purchase, PurchaseSchema]):
    def __init__(self):
        super().__init__(model=Purchase, schema=PurchaseSchema, user_dependency=None)

    def config_schemas(self, schema, **kwargs):
        super().config_schemas(schema)
        self.create_request_schema = PurchaseCreateSchema

    def config_routes(self):
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

    async def create_item(self, request: Request, item: PurchaseCreateSchema):
        return await super().create_item(request, item.model_dump())

    async def start_direct_purchase(
        self,
        request: Request,
        amount: Decimal,
        description: str,
        callback_url: str,
        test: bool = False,
    ):
        purchase: Purchase = await self.create_item(
            request,
            PurchaseCreateSchema(
                amount=amount,
                description=description,
                callback_url=callback_url,
                is_test=test,
            ),
        )
        return await self.start_purchase(request, purchase.uid)

    async def start_purchase(self, request: Request, uid: uuid.UUID):
        auth = await self.get_auth(request)
        item: Purchase = await self.get_item(
            uid, user_id=auth.user_id, business_name=auth.business.name
        )
        start_data = await start_purchase(business=auth.business, purchase=item)
        if start_data["status"]:
            return RedirectResponse(url=item.start_payment_url)

    async def verify_purchase(
        self, request: Request, uid: uuid.UUID, Status: str, Authority: str
    ):
        auth = await self.get_auth(request)
        item = await self.get_item(
            uid, user_id=auth.user_id, business_name=auth.business.name
        )
        purchase = await verify_purchase(
            business=auth.business, item=item, status=Status, authority=Authority
        )

        # TODO send transaction proposal to the business ufaas

        return RedirectResponse(url=purchase.callback_url)


router = PurchaseRouter().router
