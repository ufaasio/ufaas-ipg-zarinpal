import logging

from apps.config.models import Configuration
from fastapi_mongo_base.utils import aionetwork
from server.config import Settings
from ufaas_fastapi_business.models import Business

from .exceptions import AmountIsLessThanMinimum, PurchaseDoesNotExist, ZarinpalException
from .models import Purchase
from .schemas import ProposalCreateSchema


async def start_purchase(business: Business, purchase: Purchase) -> dict:
    callback_url = (
        f"https://{business.domain}{Settings.base_path}/purchases/{purchase.uid}/verify"
    )

    config: Configuration = await Configuration.get_config(business.name)

    data = {
        "MerchantID": config.merchant_id,
        "Amount": int(purchase.amount),
        "Description": purchase.description,
        "Mobile": purchase.phone,
        "CallbackURL": callback_url,
    }

    response = await aionetwork.aio_request(
        method="post", url=purchase.config.payment_request_url, json=data
    )
    if response["Status"] != 100:
        raise AmountIsLessThanMinimum(f"response: {response}, purchase: {purchase.uid}")

    purchase.authority = response["Authority"]
    purchase.status = "PENDING"
    await purchase.save()
    return {
        "status": True,
        "authority": purchase.authority,
    }


async def verify_purchase(
    business: Business, item: Purchase, status: str, authority: str
) -> Purchase:
    purchase: Purchase = await Purchase.get_purchase_by_authority(
        business.name, authority
    )
    if not purchase:
        raise PurchaseDoesNotExist(authority)
    if purchase.uid != item.uid:
        raise ZarinpalException(f"uid does not match for {authority}")

    if purchase.status in ["SUCCESS", "FAILED"]:
        return purchase

    if status == "NOK":
        await purchase.fail("Status is NOK")
        return purchase

    config: Configuration = await Configuration.get_config(business.name)

    data = {
        "MerchantID": config.merchant_id,
        "Amount": int(purchase.amount),
        "Authority": authority,
    }

    response = await aionetwork.aio_request(
        method="post", url=purchase.config.payment_verify_url, json=data
    )

    logging.info(f"response: {response}")

    if response["Status"] in [100, 101]:
        await purchase.success(response["RefID"])
    else:
        await purchase.fail(response["Status"])
    return purchase


async def create_proposal(purchase: Purchase, business: Business) -> dict:
    config: Configuration = await Configuration.get_config(business.name)

    proposal_data = ProposalCreateSchema(
        amount=purchase.amount,
        description=purchase.description,
        currency=Settings.currency,
        task_status="init",
        participants=[
            {"wallet_id": purchase.wallet_id, "amount": purchase.amount},
            {"wallet_id": config.income_wallet_id, "amount": -purchase.amount},
        ],
        note=None,
        meta_data=None,
    ).model_dump_json()

    access_token = await business.get_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "content-type": "application/json",
    }

    response = await aionetwork.aio_request(
        method="post",
        url=f"{business.config.core_url}api/v1/proposals/",
        data=proposal_data,
        headers=headers,
        raise_exception=False,
    )
    if "error" in response:
        logging.error(f"Error in create_proposal {response}")
        raise ZarinpalException(f"Error in create_proposal {response}")
    return response
