import tkinter as tk
from tkinter import ttk, messagebox

from portfolio import Portfolio
from rates import ASSETS
from utils import format_amount, format_rub, parse_start_amount, plain_number


class GameTab(ttk.Frame):
    """Вкладка симулятора: виртуальный портфель"""

    def __init__(self, parent, portfolio, save_path):
        super().__init__(parent)
        self.portfolio = portfolio
        self.save_path = save_path  # файл, куда сохраняем портфель
        self.rates = {}             # заполняет главное окно через set_rates

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

        # Выбор стартовой суммы и новая игра
        start_frame = ttk.Frame(self)
        start_frame.pack(pady=10)
        ttk.Label(start_frame, text="Стартовая сумма, ₽:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.entry_start = ttk.Entry(start_frame, width=14, font=("Arial", 11))
        self.entry_start.grid(row=0, column=1, padx=5)
        self.entry_start.insert(0, plain_number(portfolio.start_balance))
        ttk.Button(start_frame, text="Начать заново", command=self.restart).grid(row=0, column=2, padx=5)

        self.update_view()

    def set_rates(self, rates):
        """Главное окно присылает сюда свежие курсы"""
        self.rates = rates
        self.update_view()

    def on_enter(self):
        """На этой вкладке Enter пока ничего не делает"""

    def restart(self):
        """Новая игра с суммой из поля: старый портфель и история сделок удаляются"""
        try:
            amount = parse_start_amount(self.entry_start.get())
        except ValueError as error:
            messagebox.showerror("Ошибка", str(error))
            return

        question = (f"Начать игру заново с {format_rub(amount)}?\n"
                    "Текущий портфель и история сделок будут удалены.")
        if not messagebox.askyesno("Начать заново", question):
            return

        self.portfolio = Portfolio(cash=amount, commission=self.portfolio.commission)
        try:
            self.portfolio.save(self.save_path)
        except OSError:
            messagebox.showwarning("Внимание", "Не удалось сохранить портфель в файл.")
        self.update_view()

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
