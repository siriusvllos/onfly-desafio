"""Testes adicionais: o CLI lê todas as linhas do arquivo, sem limite."""

from helpers import run_cli


def test_reads_more_than_200_rows(tmp_path):
    """total_reservations = número de reservas no arquivo, mesmo acima de 200."""
    total = 250
    report = run_cli(
        tmp_path,
        [{"reservation_id": f"R-{index}", "amount": "10.00"} for index in range(1, total + 1)],
    )
    summary = report["summary"]
    assert summary["total_reservations"] == total
    assert summary["confirmed_reservations"] == total
    assert summary["total_room_nights"] == total
    assert summary["total_amount_brl"] == "2500.00"


def test_last_row_after_200_is_counted(tmp_path):
    """A reserva da linha 201 (única CANCELLED) precisa aparecer nas contagens."""
    rows = [{"reservation_id": f"R-{index}"} for index in range(1, 201)]
    rows.append({"reservation_id": "R-201", "status": "CANCELLED"})
    report = run_cli(tmp_path, rows)
    assert report["summary"]["total_reservations"] == 201
    assert report["summary"]["cancelled_reservations"] == 1
