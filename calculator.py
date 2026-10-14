import math
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox
import requests

FIAT_URL = "https://open.er-api.com/v6/latest/USD"
CRYPTO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"

# Запасные курсы (рублей за 1 единицу валюты)
FALLBACK_RATES = {
    "RUB": 1.0,
    "USD": 95.0,
    "EUR": 102.0,
    "BTC": 6000000.0,
    "ETH": 300000.0,
}
CURRENCIES = list(FALLBACK_RATES)

# История операций: самые новые сверху, хранится, пока открыта программа
history = []
MAX_HISTORY = 10


def get_rates():
    """Загружает курсы. Возвращает (курсы, ok): ok = True, если загрузилось всё"""
    rates = dict(FALLBACK_RATES)
    ok = True

    try:
        fiat = requests.get(FIAT_URL, timeout=5).json()["rates"]
        rates["USD"] = fiat["RUB"]
        rates["EUR"] = fiat["RUB"] / fiat["EUR"]
    except Exception as error:
        print("Ошибка загрузки валют:", repr(error))
        messagebox.showwarning("Внимание", "Не удалось загрузить курсы валют.\nИспользуются запасные значения.")
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
        messagebox.showwarning("Внимание", "Не удалось загрузить курсы BTC и ETH.\nДля них используются запасные значения.")
        ok = False

    return rates, ok


def show_status(ok):
    """Показывает внизу окна, откуда сейчас курсы"""
    if ok:
        label_status.config(text=f"Курсы обновлены в {datetime.now():%H:%M:%S}")
    else:
        label_status.config(text="Используются запасные курсы (устарели)")


def refresh():
    """Загружает курсы заново по кнопке"""
    global rates
    rates, ok = get_rates()
    show_status(ok)


def format_money(value, currency):
    """Для крипты 6 знаков после запятой, для остальных 2"""
    if currency in ("BTC", "ETH"):
        return f"{value:.6f} {currency}"
    return f"{value:.2f} {currency}"


def add_to_history(amount, from_cur, result, to_cur):
    """Добавляет запись в начало списка и обновляет список в окне"""
    line = f"{datetime.now():%H:%M}  {format_money(amount, from_cur)} → {format_money(result, to_cur)}"
    history.insert(0, line)
    del history[MAX_HISTORY:]  # оставляем только последние записи

    listbox_history.delete(0, tk.END)
    for item in history:
        listbox_history.insert(tk.END, item)


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

    label_result.config(text=f"Результат: {format_money(result, to_cur)}")
    add_to_history(amount, from_cur, result, to_cur)


def swap():
    """Меняет валюты местами и сразу пересчитывает"""
    from_cur = combo_from.get()
    combo_from.set(combo_to.get())
    combo_to.set(from_cur)
    convert()


# Сначала создаём окно: messagebox внутри get_rates требует существующий root
root = tk.Tk()
root.title("Crypto & Fiat Converter")
root.geometry("420x560")
root.resizable(False, False)

rates, rates_ok = get_rates()

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

btn_swap = ttk.Button(frame, text="⇄", width=3, command=swap)
btn_swap.grid(row=1, column=2, padx=5)

ttk.Label(frame, text="В:", font=("Arial", 10)).grid(row=0, column=3, sticky="w", padx=5)
combo_to = ttk.Combobox(frame, values=CURRENCIES, width=6, font=("Arial", 11), state="readonly")
combo_to.grid(row=1, column=3, padx=5, pady=5)
combo_to.set("RUB")

btn_convert = ttk.Button(root, text="Рассчитать конвертацию", command=convert)
btn_convert.pack(pady=15)

label_result = ttk.Label(root, text="Результат: ", font=("Arial", 13, "bold"), foreground="#107c10")
label_result.pack(pady=5)

ttk.Label(root, text="История операций:", font=("Arial", 10)).pack(pady=(10, 0))
listbox_history = tk.Listbox(root, width=48, height=10, font=("Arial", 9))
listbox_history.pack(pady=5)

btn_refresh = ttk.Button(root, text="Обновить курсы", command=refresh)
btn_refresh.pack(pady=10)

label_status = ttk.Label(root, text="", font=("Arial", 8), foreground="gray")
label_status.pack(side="bottom", pady=10)
show_status(rates_ok)

# Enter в любом месте окна запускает расчёт
root.bind("<Return>", lambda event: convert())
entry_amount.focus()

root.mainloop()
