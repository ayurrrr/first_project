import tkinter as tk
from tkinter import ttk, messagebox
import requests

FIAT_URL = "https://open.er-api.com/v6/latest/USD"

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
    """USD и EUR берём из API, крипта пока остаётся фиксированной"""
    rates = dict(FALLBACK_RATES)
    try:
        response = requests.get(FIAT_URL, timeout=5)
        response.raise_for_status()
        fiat = response.json()["rates"]  # единиц валюты за 1 USD
        rates["USD"] = fiat["RUB"]
        rates["EUR"] = fiat["RUB"] / fiat["EUR"]
    except (requests.RequestException, KeyError, ValueError):
        messagebox.showwarning(
            "Внимание",
            "Не удалось загрузить курсы.\nИспользуются запасные значения.",
        )
    return rates


def convert():
    """Конвертация по текущим курсам"""
    try:
        amount = float(entry_amount.get())
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

    except ValueError:
        messagebox.showerror("Ошибка", "Пожалуйста, введите корректное число!")


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