"""Testes adicionais: desempate do ranking de hotéis por hotel_id."""

from helpers import run_cli


def test_top_hotels_tie_is_broken_by_hotel_id_ascending(tmp_path):
    """Valores iguais ficam em hotel_id ascendente, independente da ordem no arquivo.

    O corte do --top cai no meio do empate, então também valida quais hotéis entram.
    Um `reverse=True` simples inverteria o desempate (H03, H02) e falharia aqui.
    """
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H04", "hotel_name": "Hotel D", "amount": "900.00"},
            {"reservation_id": "R-4", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "500.00"},
        ],
        top=3,
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H04", "H01", "H02"]
    assert [hotel["total_brl"] for hotel in report["top_hotels"]] == ["900.00", "500.00", "500.00"]


def test_top_hotels_tie_after_currency_conversion(tmp_path):
    """100 USD x 5,42 = 542 BRL empata exatamente com 542 BRL (Decimal, sem resíduo de float)."""
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H02", "hotel_name": "Hotel B", "currency": "USD", "amount": "100.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel A", "currency": "BRL", "amount": "542.00"},
        ],
    )
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02"]
