"""Мелкие общие функции: разбор суммы и оформление чисел."""
import math

CRYPTO = ("BTC", "ETH")
MAX_START_AMOUNT = 1_000_000_000_000  # триллион: больше не нужно, и дробные числа остаются точными


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


def parse_start_amount(text):
    """Стартовая сумма игры: положительное число, не больше триллиона"""
    value = parse_amount(text)
    if value <= 0:
        raise ValueError("Стартовая сумма должна быть больше нуля!")
    if value > MAX_START_AMOUNT:
        raise ValueError("Слишком большая сумма: максимум 1 000 000 000 000 ₽!")
    return value


def plain_number(value):
    """100000.0 -> '100000', 2500.5 -> '2500.5' (без экспоненты и лишних нулей)"""
    return f"{value:.2f}".rstrip("0").rstrip(".")


def format_amount(value, asset):
    """Для крипты 6 знаков после запятой, для остальных 2"""
    return f"{value:.6f}" if asset in CRYPTO else f"{value:.2f}"


def format_rub(value):
    """12345.6 -> '12 345.60 ₽'"""
    return f"{value:,.2f}".replace(",", " ") + " ₽"
