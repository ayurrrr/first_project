import tkinter as tk
from tkinter import ttk, messagebox

from portfolio import Portfolio, TradeError
from rates import ASSETS, FALLBACK_RATES
from utils import format_amount, format_rub, parse_amount, parse_start_amount, plain_number

COMMISSION = 0.001  # комиссия за каждую сделку: 0.001 = 0.1% от суммы


class GameTab(ttk.Frame):
    """Вкладка симулятора: виртуальный портфель"""

    def __init__(self, parent, portfolio, save_path):
        super().__init__(parent)
        self.portfolio = portfolio
        self.portfolio.commission = COMMISSION  # комиссия задаётся здесь, в файл она не влияет
        self.save_path = save_path  # файл, куда сохраняем портфель
        self.rates = {}             # заполняет главное окно через set_rates
        self.value_history = []     # стоимость портфеля после каждого обновления курсов
        self.chart_colors = {"field": "#ffffff", "result": "#107c10", "hint": "gray"}

        ttk.Label(self, text="Торговый симулятор", font=("Arial", 14, "bold")).pack(pady=(15, 2))
        self.label_hint = ttk.Label(self, text=f"Виртуальные деньги, реальные курсы. Комиссия {COMMISSION * 100:g}%", font=("Arial", 9))
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
        self.table.pack(pady=(10, 5), padx=10)

        # Торговля: выбираем актив, вводим количество, жмём кнопку
        trade_frame = ttk.Frame(self)
        trade_frame.pack(pady=(5, 5))
        ttk.Label(trade_frame, text="Актив:", font=("Arial", 10)).grid(row=0, column=0, padx=5)
        self.combo_asset = ttk.Combobox(trade_frame, values=ASSETS, width=6,
                                        state="readonly", font=("Arial", 11))
        self.combo_asset.set(ASSETS[0])
        self.combo_asset.grid(row=0, column=1, padx=5)
        ttk.Label(trade_frame, text="Количество:", font=("Arial", 10)).grid(row=0, column=2, padx=5)
        self.entry_trade = ttk.Entry(trade_frame, width=12, font=("Arial", 11))
        self.entry_trade.grid(row=0, column=3, padx=5)
        self.entry_trade.bind("<KeyRelease>", lambda event: self.update_cost())
        self.combo_asset.bind("<<ComboboxSelected>>", lambda event: self.update_cost())

        self.label_cost = ttk.Label(self, text="", font=("Arial", 10))
        self.label_cost.pack(pady=2)

        buttons = ttk.Frame(self)
        buttons.pack(pady=5)
        ttk.Button(buttons, text="Купить", command=self.buy).grid(row=0, column=0, padx=5)
        ttk.Button(buttons, text="Продать", command=self.sell).grid(row=0, column=1, padx=5)
        ttk.Button(buttons, text="Продать всё", command=self.sell_all).grid(row=0, column=2, padx=5)

        # История сделок: новые сверху
        ttk.Label(self, text="История сделок", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        history_frame = ttk.Frame(self)
        history_frame.pack(padx=10)
        self.history = ttk.Treeview(history_frame, columns=("time", "side", "asset", "qty", "total"),
                                    show="headings", height=3)
        for column, title, width in (("time", "Время", 120), ("side", "Сделка", 80),
                                     ("asset", "Актив", 60), ("qty", "Количество", 100),
                                     ("total", "Сумма", 110)):
            self.history.heading(column, text=title)
            self.history.column(column, width=width, anchor="center")
        scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history.yview)
        self.history.configure(yscrollcommand=scroll.set)
        self.history.pack(side="left")
        scroll.pack(side="left", fill="y")

        # График стоимости портфеля
        ttk.Label(self, text="Стоимость портфеля", font=("Arial", 10, "bold")).pack(pady=(10, 2))
        self.chart = tk.Canvas(self, width=440, height=100, highlightthickness=0)
        self.chart.pack()

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
        self.add_point()
        self.update_view()

    def add_point(self):
        """Запоминает текущую стоимость портфеля для графика"""
        if self.rates == FALLBACK_RATES:  # запасные курсы выдуманные, их на график не берём
            return
        self.value_history.append(self.portfolio.value(self.rates))
        if len(self.value_history) > 60:  # храним только последние 60 точек
            self.value_history.pop(0)

    def draw_chart(self):
        """Рисует линию стоимости портфеля"""
        self.chart.delete("all")
        self.chart.config(bg=self.chart_colors["field"])
        if len(self.value_history) < 2:
            self.chart.create_text(220, 50, text="График появится после нескольких обновлений курсов",
                                   fill=self.chart_colors["hint"])
            return

        width, height, margin = 440, 100, 15
        low = min(self.value_history)
        high = max(self.value_history)
        if high == low:  # стоимость не менялась: рисуем ровную линию
            high = low + 1

        points = []
        last = len(self.value_history) - 1
        for i, value in enumerate(self.value_history):
            x = margin + (width - 2 * margin) * i / last
            y = height - margin - (height - 2 * margin) * (value - low) / (high - low)
            points.extend([x, y])
        self.chart.create_line(*points, fill=self.chart_colors["result"], width=2)
        self.chart.create_text(5, 8, text=format_rub(max(self.value_history)), anchor="w",
                               fill=self.chart_colors["hint"], font=("Arial", 8))
        self.chart.create_text(5, height - 8, text=format_rub(min(self.value_history)), anchor="w",
                               fill=self.chart_colors["hint"], font=("Arial", 8))

    def on_enter(self):
        """Enter на этой вкладке тоже ничего не делает: покупать надо кнопкой"""

    def update_cost(self):
        """Показывает, сколько рублей стоит введённое количество"""
        asset = self.combo_asset.get()
        try:
            amount = parse_amount(self.entry_trade.get())
        except ValueError:
            self.label_cost.config(text="")
            return
        if asset in self.rates:
            cost = amount * self.rates[asset]
            self.label_cost.config(text=f"Это примерно {format_rub(cost)} (комиссия {format_rub(cost * COMMISSION)})")

    def trade(self, side):
        """Общая часть покупки и продажи: читаем форму, делаем сделку, сохраняем"""
        if not self.rates:
            messagebox.showwarning("Внимание", "Курсы ещё не загружены.")
            return
        asset = self.combo_asset.get()
        try:
            amount = parse_amount(self.entry_trade.get())
            if amount <= 0:
                raise ValueError("Введите количество больше нуля.")
            if side == "buy":
                self.portfolio.buy(asset, amount, self.rates[asset])
            else:
                self.portfolio.sell(asset, amount, self.rates[asset])
        except (ValueError, TradeError) as error:
            messagebox.showerror("Ошибка", str(error))
            return
        self.after_trade()

    def after_trade(self):
        """Сохраняем портфель, чистим поле и обновляем цифры"""
        try:
            self.portfolio.save(self.save_path)
        except OSError:
            messagebox.showwarning("Внимание", "Не удалось сохранить портфель в файл.")
        self.entry_trade.delete(0, tk.END)
        self.label_cost.config(text="")
        self.add_point()
        self.update_view()

    def buy(self):
        self.trade("buy")

    def sell(self):
        self.trade("sell")

    def sell_all(self):
        """Продаёт всё количество выбранного актива"""
        asset = self.combo_asset.get()
        qty = self.portfolio.holdings.get(asset, 0.0)
        if qty <= 0:
            messagebox.showinfo("Нечего продавать", f"У вас нет {asset}.")
            return
        try:
            self.portfolio.sell(asset, qty, self.rates[asset])
        except TradeError as error:
            messagebox.showerror("Ошибка", str(error))
            return
        self.after_trade()

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

        self.portfolio = Portfolio(cash=amount, commission=COMMISSION)
        self.value_history = []  # новая игра: старый график не нужен
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

        self.update_history()
        self.draw_chart()

    def update_history(self):
        """Заполняет таблицу сделок: самые новые сверху"""
        self.history.delete(*self.history.get_children())
        for trade in reversed(self.portfolio.trades):
            when = trade["time"][5:16].replace("T", " ")  # "10-21 01:45"
            side = "Покупка" if trade["side"] == "buy" else "Продажа"
            self.history.insert("", tk.END, values=(
                when, side, trade["asset"],
                format_amount(trade["amount"], trade["asset"]),
                format_rub(trade["total"]),
            ))

    def apply_colors(self, colors):
        """Цвета таблицы задаются стилем Treeview в главном окне, тут красить нечего"""
        self.label_hint.config(foreground=colors["hint"])
        self.chart_colors = colors
        self.draw_chart()