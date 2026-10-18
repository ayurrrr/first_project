"""Мелкие общие функции: разбор суммы и оформление чисел."""
import math

CRYPTO = ("BTC", "ETH")


def parse_amount(text):
    """Превращает строку в сумму. При ошибке бросает ValueError с понятным текстом"""
    try:
        value = float(text.strip().replace(",", "."))  # 100,5 -> 100.5
    except ValueError:
        raise ValueError("Пожалуйста, введите корректное число!")
    if not math.isfinite(value):  # nan и inf тоже превращаются в числа
        raise ValueError("Пожалуйста, введите корректное число!")
    if value < 0:
        raise ValueError("Сумма не может быть отрицательной!")
    return value


def format_amount(value, asset):
    """Для крипты 6 знаков после запятой, для остальных 2"""
    return f"{value:.6f}" if asset in CRYPTO else f"{value:.2f}"


def format_rub(value):
    """12345.6 -> '12 345.60 ₽'"""
    return f"{value:,.2f}".replace(",", " ") + " ₽"
