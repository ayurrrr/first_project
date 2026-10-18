import tkinter as tk
from tkinter import ttk

from rates import ASSETS
from utils import format_amount, format_rub


class GameTab(ttk.Frame):
    """Вкладка симулятора: виртуальный портфель"""

    def __init__(self, parent, portfolio):
        super().__init__(parent)
        self.portfolio = portfolio
        self.rates = {}  # заполняет главное окно через set_rates

        ttk.Label(self, text="Торговый симулятор", font=("Arial", 14, "bold")).pack(pady=(15, 2))
        self.label_hint = ttk.Label(self, text="Виртуальные деньги, реальные курсы", font=("Arial", 9))
        self.label_hint.pack()

        self.label_cash = ttk.Label(self, text="", font=("Arial", 12))
        self.label_cash.pack(pady=(15, 2))
        self.label_value = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.label_value.pack(pady=2)
        self.label_profit = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.label_profit.pack(pady=2)

        self.table = ttk.Treeview(self, columns=("asset", "qty", "rate", "value"),
                                  show="headings", height=4)
        for column, title, width in (("asset", "Актив", 60), ("qty", "Количество", 110),
                                     ("rate", "Курс", 130), ("value", "Стоимость", 130)):
            self.table.heading(column, text=title)
            self.table.column(column, width=width, anchor="center")
        self.table.pack(pady=15, padx=10)

        self.update_view()

    def set_rates(self, rates):
        """Главное окно присылает сюда свежие курсы"""
        self.rates = rates
        self.update_view()

    def on_enter(self):
        """На этой вкладке Enter пока ничего не делает"""

    def update_view(self):
        """Перерисовывает все цифры на вкладке"""
        if not self.rates:  # курсы ещё не пришли
            return

        self.label_cash.config(text=f"Свободные рубли: {format_rub(self.portfolio.cash)}")
        self.label_value.config(text=f"Стоимость портфеля: {format_rub(self.portfolio.value(self.rates))}")

        profit = self.portfolio.profit(self.rates)
        sign = "+" if profit > 0 else ""
        color = "#107c10" if profit > 0 else "#c42b1c" if profit < 0 else "gray"
        self.label_profit.config(text=f"Прибыль / убыток: {sign}{format_rub(profit)}", foreground=color)

        self.table.delete(*self.table.get_children())
        for asset in ASSETS:
            qty = self.portfolio.holdings.get(asset, 0.0)
            self.table.insert("", tk.END, values=(
                asset,
                format_amount(qty, asset),
                format_rub(self.rates[asset]),
                format_rub(qty * self.rates[asset]),
            ))

    def apply_colors(self, colors):
        """Цвета таблицы задаются стилем Treeview в главном окне, тут красить нечего"""
        self.label_hint.config(foreground=colors["hint"])
