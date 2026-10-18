import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

from rates import CURRENCIES
from utils import format_amount, parse_amount

MAX_HISTORY = 10


class ConverterTab(ttk.Frame):
    """Вкладка конвертера валют"""

    def __init__(self, parent):
        super().__init__(parent)
        self.rates = {}    # заполняет главное окно через set_rates
        self.history = []  # последние операции, новые сверху

        ttk.Label(self, text="Крипто-Валютный Конвертер", font=("Arial", 14, "bold")).pack(pady=15)

        frame = ttk.Frame(self)
        frame.pack(pady=10)

        ttk.Label(frame, text="Сумма:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5)
        self.entry_amount = ttk.Entry(frame, width=18, font=("Arial", 12))
        self.entry_amount.grid(row=1, column=0, padx=5, pady=5)
        self.entry_amount.insert(0, "100")

        ttk.Label(frame, text="Из:", font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=5)
        self.combo_from = ttk.Combobox(frame, values=CURRENCIES, width=6, font=("Arial", 11), state="readonly")
        self.combo_from.grid(row=1, column=1, padx=5, pady=5)
        self.combo_from.set("USD")

        ttk.Button(frame, text="⇄", width=3, command=self.swap).grid(row=1, column=2, padx=5)

        ttk.Label(frame, text="В:", font=("Arial", 10)).grid(row=0, column=3, sticky="w", padx=5)
        self.combo_to = ttk.Combobox(frame, values=CURRENCIES, width=6, font=("Arial", 11), state="readonly")
        self.combo_to.grid(row=1, column=3, padx=5, pady=5)
        self.combo_to.set("RUB")

        ttk.Button(self, text="Рассчитать конвертацию", command=self.convert).pack(pady=15)

        self.label_result = ttk.Label(self, text="Результат: ", font=("Arial", 13, "bold"))
        self.label_result.pack(pady=5)

        ttk.Label(self, text="История операций:", font=("Arial", 10)).pack(pady=(10, 0))
        self.listbox_history = tk.Listbox(self, width=48, height=9, font=("Arial", 9))
        self.listbox_history.pack(pady=5)

        self.entry_amount.focus()

    def set_rates(self, rates):
        """Главное окно присылает сюда свежие курсы"""
        self.rates = rates

    def on_enter(self):
        """Enter, нажатый на этой вкладке, запускает расчёт"""
        self.convert()

    def convert(self):
        """Конвертация по текущим курсам"""
        try:
            amount = parse_amount(self.entry_amount.get())
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))
            return

        from_cur = self.combo_from.get()
        to_cur = self.combo_to.get()

        # Сначала в рубли, потом из рублей в нужную валюту
        result = amount * self.rates[from_cur] / self.rates[to_cur]

        self.label_result.config(text=f"Результат: {format_amount(result, to_cur)} {to_cur}")
        self.add_to_history(amount, from_cur, result, to_cur)

    def swap(self):
        """Меняет валюты местами и сразу пересчитывает"""
        from_cur = self.combo_from.get()
        self.combo_from.set(self.combo_to.get())
        self.combo_to.set(from_cur)
        self.convert()

    def add_to_history(self, amount, from_cur, result, to_cur):
        """Добавляет запись в начало списка и обновляет список в окне"""
        line = (f"{datetime.now():%H:%M}  {format_amount(amount, from_cur)} {from_cur}"
                f" → {format_amount(result, to_cur)} {to_cur}")
        self.history.insert(0, line)
        del self.history[MAX_HISTORY:]  # оставляем только последние записи

        self.listbox_history.delete(0, tk.END)
        for item in self.history:
            self.listbox_history.insert(tk.END, item)

    def apply_colors(self, colors):
        """Перекрашивает элементы, которые не подчиняются ttk-стилям"""
        self.listbox_history.config(bg=colors["field"], fg=colors["fg"])
        self.label_result.config(foreground=colors["result"])
