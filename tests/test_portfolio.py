import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from portfolio import Portfolio, TradeError, START_BALANCE  # noqa: E402

RATES = {"RUB": 1.0, "USD": 100.0, "BTC": 5_000_000.0}


def test_start_state():
    p = Portfolio()
    assert p.cash == START_BALANCE == 100_000
    assert p.holdings == {} and p.trades == []


def test_buy():
    p = Portfolio()
    p.buy("USD", 10, 100.0)
    assert p.cash == 99_000
    assert p.holdings == {"USD": 10}
    assert p.trades[0]["side"] == "buy" and p.trades[0]["total"] == 1000


def test_buy_adds_to_existing():
    p = Portfolio()
    p.buy("USD", 10, 100.0)
    p.buy("USD", 5, 110.0)
    assert p.holdings["USD"] == 15
    assert p.cash == pytest.approx(100_000 - 1000 - 550)


def test_buy_not_enough_money():
    p = Portfolio()
    with pytest.raises(TradeError, match="Не хватает"):
        p.buy("BTC", 1, 5_000_000.0)
    assert p.cash == 100_000 and p.holdings == {} and p.trades == []


def test_buy_exactly_all_money():
    p = Portfolio()
    p.buy("USD", 1000, 100.0)
    assert p.cash == 0


def test_sell():
    p = Portfolio()
    p.buy("USD", 10, 100.0)
    p.sell("USD", 4, 110.0)
    assert p.holdings["USD"] == 6
    assert p.cash == pytest.approx(99_000 + 440)


def test_sell_all_removes_asset():
    p = Portfolio()
    p.buy("USD", 10, 100.0)
    p.sell("USD", 10, 100.0)
    assert "USD" not in p.holdings
    assert p.cash == pytest.approx(100_000)


def test_sell_more_than_have():
    p = Portfolio()
    p.buy("USD", 10, 100.0)
    with pytest.raises(TradeError, match="только"):
        p.sell("USD", 11, 100.0)
    assert p.holdings["USD"] == 10 and len(p.trades) == 1


def test_sell_what_you_dont_have():
    with pytest.raises(TradeError):
        Portfolio().sell("ETH", 1, 300_000.0)


@pytest.mark.parametrize("amount", [0, -1, float("nan"), float("inf")])
def test_bad_amount(amount):
    with pytest.raises(TradeError):
        Portfolio().buy("USD", amount, 100.0)


@pytest.mark.parametrize("price", [0, -5, float("nan")])
def test_bad_price(price):
    with pytest.raises(TradeError):
        Portfolio().buy("USD", 1, price)


def test_float_crumbs_do_not_block_sell_all():
    p = Portfolio()
    for _ in range(10):
        p.buy("BTC", 0.01, 1_000_000.0)  # 0.1 из десяти покупок по 0.01 в точности не равно 0.1
    p.sell("BTC", 0.1, 1_000_000.0)
    assert "BTC" not in p.holdings


def test_commission():
    p = Portfolio(commission=0.01)
    p.buy("USD", 10, 100.0)  # 1000 + 1% = 1010
    assert p.cash == pytest.approx(100_000 - 1010)
    p.sell("USD", 10, 100.0)  # 1000 - 1% = 990
    assert p.cash == pytest.approx(100_000 - 1010 + 990)


def test_value_and_profit():
    p = Portfolio()
    p.buy("USD", 100, 100.0)  # потратили 10 000
    assert p.value(RATES) == pytest.approx(100_000)
    assert p.profit(RATES) == pytest.approx(0)
    rates_up = dict(RATES, USD=110.0)
    assert p.profit(rates_up) == pytest.approx(1000)
    rates_down = dict(RATES, USD=90.0)
    assert p.profit(rates_down) == pytest.approx(-1000)


def test_save_and_load(tmp_path):
    path = tmp_path / "portfolio.json"
    p = Portfolio(commission=0.001)
    p.buy("USD", 10, 100.0)
    p.save(path)
    loaded = Portfolio.load(path)
    assert loaded.cash == p.cash and loaded.holdings == p.holdings
    assert loaded.trades == p.trades and loaded.commission == 0.001


def test_load_missing_file_gives_new_portfolio(tmp_path):
    p = Portfolio.load(tmp_path / "nothing.json")
    assert p.cash == START_BALANCE


def test_load_broken_file_raises(tmp_path):
    path = tmp_path / "portfolio.json"
    path.write_text("{сломано", encoding="utf-8")
    with pytest.raises(ValueError):
        Portfolio.load(path)


def test_load_wrong_structure_raises(tmp_path):
    path = tmp_path / "portfolio.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")  # корректный JSON, но не портфель
    with pytest.raises((KeyError, TypeError)):
        Portfolio.load(path)
