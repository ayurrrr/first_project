"""Виртуальный портфель: рубли и купленные активы."""
import json
import math
from datetime import datetime
from pathlib import Path

START_BALANCE = 100_000.0
EPS = 1e-9  # допуск на ошибки округления дробных чисел


class TradeError(Exception):
    """Ошибка сделки. Текст понятен пользователю и показывается в окне."""


class Portfolio:
    def __init__(self, cash=START_BALANCE, commission=0.0):
        self.start_balance = cash
        self.cash = cash
        self.commission = commission  # доля от суммы сделки: 0.001 = 0.1%
        self.holdings = {}  # актив -> количество
        self.trades = []    # история сделок, новые в конце

    def buy(self, asset, amount, price):
        """Покупает amount единиц актива по цене price (рублей за единицу)"""
        self._check(amount, price)
        cost = amount * price
        total = cost + cost * self.commission
        if total > self.cash + EPS:
            raise TradeError(f"Не хватает рублей: нужно {total:.2f}, есть {self.cash:.2f}")

        self.cash = max(0.0, self.cash - total)
        self.holdings[asset] = self.holdings.get(asset, 0.0) + amount
        self._record("buy", asset, amount, price, total)

    def sell(self, asset, amount, price):
        """Продаёт amount единиц актива по цене price"""
        self._check(amount, price)
        held = self.holdings.get(asset, 0.0)
        if amount > held + EPS:
            raise TradeError(f"В портфеле только {held:g} {asset}, а продать хотите {amount:g}")

        amount = min(amount, held)  # убираем крошечную ошибку округления
        proceeds = amount * price
        total = proceeds - proceeds * self.commission

        self.cash += total
        left = held - amount
        if left <= EPS:
            self.holdings.pop(asset, None)
        else:
            self.holdings[asset] = left
        self._record("sell", asset, amount, price, total)

    def value(self, rates):
        """Полная стоимость портфеля в рублях: деньги плюс все активы по текущим курсам"""
        assets_value = sum(qty * rates[asset] for asset, qty in self.holdings.items())
        return self.cash + assets_value

    def profit(self, rates):
        """Прибыль (плюс) или убыток (минус) относительно стартовой суммы"""
        return self.value(rates) - self.start_balance

    def _check(self, amount, price):
        if not math.isfinite(amount) or amount <= 0:
            raise TradeError("Количество должно быть больше нуля")
        if not math.isfinite(price) or price <= 0:
            raise TradeError("Некорректный курс")

    def _record(self, side, asset, amount, price, total):
        self.trades.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "side": side,
            "asset": asset,
            "amount": amount,
            "price": price,
            "total": total,  # сколько рублей потрачено (buy) или получено (sell), с комиссией
        })

    # --- Сохранение и загрузка ---

    def to_dict(self):
        return {
            "start_balance": self.start_balance,
            "cash": self.cash,
            "commission": self.commission,
            "holdings": self.holdings,
            "trades": self.trades,
        }

    @classmethod
    def from_dict(cls, data):
        portfolio = cls(cash=data["start_balance"], commission=data["commission"])
        portfolio.cash = data["cash"]
        portfolio.holdings = dict(data["holdings"])
        portfolio.trades = list(data["trades"])
        return portfolio

    def save(self, path):
        Path(path).write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @classmethod
    def load(cls, path):
        """Читает портфель из файла. Если файла нет, создаёт новый со стартовыми 100 000 ₽.
        Если файл повреждён, бросает ValueError, KeyError или TypeError."""
        path = Path(path)
        if not path.exists():
            return cls()
        return cls.from_dict(json.loads(path.read_text(encoding="utf-8")))
