import requests
from config import CRYPTOBOT_TOKEN


def create_invoice(amount_usdt: float, order_id: int):
    url = "https://pay.crypt.bot/api/createInvoice"

    headers = {
        "Crypto-Pay-API-Token": CRYPTOBOT_TOKEN
    }

    payload = {
        "asset": "USDT",
        "amount": amount_usdt,
        "description": f"Заказ #{order_id}",
        "payload": str(order_id),
        "allow_anonymous": True
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    if not data.get("ok"):
        raise Exception(f"Ошибка при создании инвойса: {data}")

    return data["result"]["pay_url"]
