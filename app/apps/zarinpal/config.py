class ZarinpalConfig:
    def __init__(self, test: bool = False):
        self.test = test

    @property
    def sandbox(self) -> str:
        return "sandbox" if self.test else "www"

    @property
    def payment_request_url(self) -> str:
        return (
            f"https://{self.sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
        )

    @property
    def payment_verify_url(self) -> str:
        return f"https://{self.sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"

    @property
    def start_payment_url(self) -> str:
        return f"https://{self.sandbox}.zarinpal.com/pg/StartPay"
