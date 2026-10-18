"""Загрузка курсов. Без окон и сообщений: только данные."""
import requests

FIAT_URL = "https://open.er-api.com/v6/latest/USD"
CRYPTO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

# Активы, которыми можно торговать в симуляторе
ASSETS = ["USD", "EUR", "BTC", "ETH"]
# Все валюты конвертера: рубли плюс активы
CURRENCIES = ["RUB"] + ASSETS

# Запасные курсы (рублей за 1 единицу валюты), если сеть недоступна
FALLBACK_RATES = {
    "RUB": 1.0,
    "USD": 95.0,
    "EUR": 102.0,
    "BTC": 6000000.0,
    "ETH": 300000.0,
}


def get_rates():
    """Возвращает (курсы, ok). Курсы: сколько рублей стоит 1 единица.
    ok = True, если всё загрузилось из интернета."""
    rates = dict(FALLBACK_RATES)

    try:
        fiat = requests.get(FIAT_URL, timeout=5).json()["rates"]
        rates["USD"] = fiat["RUB"]
        rates["EUR"] = fiat["RUB"] / fiat["EUR"]
    except Exception as error:
        print("Ошибка загрузки валют:", repr(error))
        return rates, False

    response = None
    try:
        response = requests.get(CRYPTO_URL, timeout=5)
        crypto = response.json()
        rates["BTC"] = crypto["bitcoin"]["usd"] * rates["USD"]
        rates["ETH"] = crypto["ethereum"]["usd"] * rates["USD"]
    except Exception as error:
        print("Ошибка загрузки крипты:", repr(error))
        if response is not None:
            print("Ответ сайта:", response.text[:300])
        return rates, False

    return rates, True
