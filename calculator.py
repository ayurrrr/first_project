import math
import tkinter as tk
from tkinter import ttk, messagebox
import requests

FIAT_URL = "https://open.er-api.com/v6/latest/USD"
CRYPTO_URL = "https://min-api.cryptocompare.com/data/pricemulti"

# Запасные курсы (рублей за 1 единицу валюты)
FALLBACK_RATES = {
    "RUB": 1.0,
    "USD": 95.0,
    "EUR": 102.0,
    "BTC": 6000000.0,
    "ETH": 300000.0,
}
CURRENCIES = list(FALLBACK_RATES)


def get_rates():
    """Загружает курсы: обычные валюты и крипту. При ошибке возвращает запасные"""
    try:
        # Обычные валюты: сколько единиц валюты в 1 USD
        response = requests.get(FIAT_URL, timeout=5)
        response.raise_for_status()
        fiat = response.json()["rates"]

        # Крипта: цена BTC и ETH в долларах
        response = requests.get(
            CRYPTO_URL, params={"fsyms": "BTC,ETH", "tsyms": "USD"}, timeout=5
        )
        response.raise_for_status()
        crypto = response.json()

        usd_rub = fiat["RUB"]
        return {
            "RUB": 1.0,
            "USD": usd_rub,
            "EUR": usd_rub / fiat["EUR"],
            "BTC": crypto["BTC"]["USD"] * usd_rub,
            "ETH": crypto["ETH"]["USD"] * usd_rub,
        }
    except (requests.RequestException, KeyError, ValueError):
        messagebox.showwarning(
            "Внимание",
            "Не удалось загрузить курсы.\nИспользуются запасные значения.",
        )
        return dict(FALLBACK_RATES)


def convert():
    """Конвертация по текущим курсам"""
    # Разрешаем запятую: 100,5 -> 100.5
    text = entry_amount.get().strip().replace(",", ".")
    try:
        amount = float(text)
    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число!")
        return

    # float("nan") и float("inf") тоже превращаются в числа, их отсекаем
    if not math.isfinite(amount):
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число!")
        return

    if amount < 0:
        messagebox.showwarning("Предупреждение", "Сумма не может быть отрицательной!")
        return

    from_cur = combo_from.get()
    to_cur = combo_to.get()

    result = amount * rates[from_cur] / rates[to_cur]

    if to_cur in ("BTC", "ETH"):
        label_result.config(text=f"Результат: {result:.6f} {to_cur}")
    else:
        label_result.config(text=f"Результат: {result:.2f} {to_cur}")


# Сначала создаём окно: messagebox внутри get_rates требует существующий root
root = tk.Tk()
root.title("Crypto & Fiat Converter")
root.geometry("400x320")
root.resizable(False, False)

rates = get_rates()

style = ttk.Style()
style.theme_use("clam")

label_title = ttk.Label(root, text="Крипто-Валютный Конвертер", font=("Arial", 14, "bold"))
label_title.pack(pady=15)

frame = ttk.Frame(root)
frame.pack(pady=10)

ttk.Label(frame, text="Сумма:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
entry_amount = ttk.Entry(frame, width=18, font=("Arial", 12))
entry_amount.grid(row=1, column=0, padx=5, pady=5)
entry_amount.insert(0, "100")

ttk.Label(frame, text="Из:", font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=5)
combo_from = ttk.Combobox(frame, values=CURRENCIES, width=6, font=("Arial", 11), state="readonly")
combo_from.grid(row=1, column=1, padx=5, pady=5)
combo_from.set("USD")

label_arrow = ttk.Label(frame, text="→", font=("Arial", 14))
label_arrow.grid(row=1, column=2, padx=5)

ttk.Label(frame, text="В:", font=("Arial", 10)).grid(row=0, column=3, sticky="w", padx=5)
combo_to = ttk.Combobox(frame, values=CURRENCIES, width=6, font=("Arial", 11), state="readonly")
combo_to.grid(row=1, column=3, padx=5, pady=5)
combo_to.set("RUB")

btn_convert = ttk.Button(root, text="Рассчитать конвертацию", command=convert)
btn_convert.pack(pady=20)

label_result = ttk.Label(root, text="Результат: ", font=("Arial", 13, "bold"), foreground="#107c10")
label_result.pack(pady=10)

root.mainloop()