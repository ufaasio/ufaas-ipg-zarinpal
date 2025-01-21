from fastapi_mongo_base.core import exceptions


class ZarinpalException(exceptions.BaseHTTPException):
    """
    BaseClass for exceptions
    """

    def __init__(self, message: str = None):
        super().__init__(400, "zarinpal_exception", message)


class PurchaseDoesNotExist(ZarinpalException):
    """No purchase submitted with this authority"""

    def __init__(self, authority: str):
        super().__init__(f"No purchase submitted with this authority: {authority}")


class PurchaseDataIsNotValid(ZarinpalException):
    """The data was not valid for Zarinpal gateway"""

    def __init__(self, data: str):
        super().__init__(f"The data was not valid for Zarinpal gateway: {data}")


class CouldNotStartPurchase(ZarinpalException):
    """did not get start authority from Zarinpal"""

    def __init__(self, response: str):
        super().__init__(f"did not get start authority from Zarinpal: {response}")


class AmountIsLessThanMinimum(ZarinpalException):
    """minimum amount to start purchase is 1000"""

    def __init__(self, amount: int):
        super().__init__(f"minimum amount to start purchase is 1000: {amount}")


class CallBackUrlNotSet(ZarinpalException):
    """Specify ZARINPAL_CALLBACK_URL in settings"""

    def __init__(self, callback_url: str):
        super().__init__(f"Specify ZARINPAL_CALLBACK_URL in settings: {callback_url}")


class MerchantIdNotSet(ZarinpalException):
    """Specify ZARINPAL_MERCHANT_ID in settings"""

    def __init__(self, merchant_id: str):
        super().__init__(f"Specify ZARINPAL_MERCHANT_ID in settings: {merchant_id}")
