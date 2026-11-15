"""Testes adicionais: conversão EUR -> BRL."""

from decimal import Decimal

from helpers import run_cli

from onfly_report.services.currency_converter import convert_to_brl

RATES = {"BRL": Decimal("1.000000"), "USD": Decimal("5.420000"), "EUR": Decimal("5.880000")}


def test_eur_conversion_multiplies_by_rate():
    """150 EUR x 5,88 = 882 BRL (mesmo caso do H09 na amostra de validação)."""
    assert convert_to_brl(Decimal("150.00"), "EUR", RATES) == Decimal("882.00")


def test_eur_conversion_is_exact_decimal():
    """Sem passar por float: o produto deve ser exato, sem arredondamento intermediário."""
    result = convert_to_brl(Decimal("19.99"), "EUR", RATES)
    assert isinstance(result, Decimal)
    assert result == Decimal("117.5412")


def test_eur_conversion_in_report(tmp_path):
    """No relatório, EUR é convertido e somado a BRL; arredonda só na serialização."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": "BRL", "amount": "100.00"},
            {"reservation_id": "R-2", "currency": "EUR", "amount": "19.99"},
            {"reservation_id": "R-3", "currency": "EUR", "amount": "19.99"},
        ],
    )
    # 100 + 2 x 117.5412 = 335.0824 -> "335.08"
    assert report["summary"]["total_amount_brl"] == "335.08"
