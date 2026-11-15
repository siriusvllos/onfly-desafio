"""Testes adicionais: noites de quarto na virada de ano."""

from datetime import date

from helpers import run_cli

from onfly_report.services.stay_calculator import calculate_room_nights


def test_calculate_room_nights_across_year_boundary():
    """30/12 -> 02/01 = 3 noites; com 2 quartos, 6 noites de quarto."""
    assert calculate_room_nights(date(2024, 12, 30), date(2025, 1, 2), 2) == 6


def test_nights_across_year_boundary_in_report(tmp_path):
    """No relatório, as noites atravessam o ano e a reserva cai no mês do check-in."""
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "checkin_date": "2024-12-30",
                "checkout_date": "2025-01-02",
                "rooms": "2",
                "amount": "600.00",
            }
        ],
    )
    assert report["summary"]["total_room_nights"] == 6
    assert report["summary"]["average_nightly_rate_brl"] == "100.00"
    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 1, "room_nights": 6, "total_brl": "600.00"}
    ]
