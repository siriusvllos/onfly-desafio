# README-ENTREGA — Desafio Onfly de Consolidador de reservas de hotel

## Resumo
O CLI gerava números errados e não passava nos testes por causa de quatro defeitos no código fonte; além disso, havia um defeito adicional que impactaria no relatório gerado. Ao corrigir os defeitos, os 5 testes originais começaram a passar rapidamente e foram adicionados 9 outros testes: os 14 foram completados sem problema.
Os testes originais não foram alterados; a amostra de validação bate com o esperado, disponibilizado no README.md do desafio, e o teste feito com o arquivo de reservas também foi conferido.
## Defeitos corrigidos

| # | Defeito | Arquivo | Causa raiz | Testes |
|-|-|-|-|-|
| 1 | Conversão de câmbio errada | services/currency_converter.py | O valor estava sendo dividido pela taxa ao invés de multiplicado, conforme definido nas regras de negócio, e passado por float ao invés de Decimal. | test_currency*.py |
| 2 | Cálculo de noites errado | services/stay_calculator.py | O cálculo subtraía só o dia do mês, ignorando a diferença real entre as datas que poderia variar entre mês e ano. | test_nights*.py) |
| 3 | NO_SHOW contado como faturável | services/status_policy.py | A regra era status != "CANCELLED", que incluía NO_SHOW, mesmo que as regras de negócio colocassem só CONFIRMED como faturável. | test_status_rules.py |
| 4 | Ranking de hotéis em ordem crescente | services/report_builder.py | A chave de ordenação (amount, hotel_id) ordenava o valor em ordem crescente, quando deve ser decrescente, e com desempate por hotel_id crescente. | test_top_hotels*.py |
| 5 | Leitura do arquivo parava em 200 linhas | repositories/csv_reservation_repository.py | Um _if len(rows) == 200: break_ descartava todas as reservas depois do índice 200. | test_read_all_rows.py |

### Correções aplicadas

    # 1. currency_converter.py
    return amount * rates[currency]

    # 2. stay_calculator.py
    return (checkout - checkin).days * rooms

    # 3. status_policy.py
    return status == "CONFIRMED"

    # 4. report_builder.py
    ranked_hotels = sorted(hotels.items(), key=lambda item: (-item[1]["amount"], item[0]))

    # 5. csv_reservation_repository.py
    return [RawRow(line_number=reader.line_num, values=values) for values in reader]

### Testes adicionados

| Arquivo | Teste executado |
|-|-|
| tests/test_currency_eur.py | EUR p/ BRL multiplicando pela taxa (150 × 5,88 = 882,00); produto exato em Decimal (19,99 × 5,88 = 117,5412); arredondamento só na serialização (335,0824 → `"335.08"`) |
| tests/test_nights_year_boundary.py | Virada de ano: 30/12/2024 - 02/01/2025 com 2 quartos = 6 noites; by_month usa o mês do check-in (2024-12) |
| tests/test_top_hotels_tiebreak.py | Desempate por hotel_id crescente; empate exato após conversão (100 USD = 542 BRL) |
| tests/test_reads_all_rows.py | Leitura de mais de 200 linhas; reserva na linha 201 entra nas contagens |

### Como validar

    python3.11 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements-dev.txt

    # testes
    pytest -q

    # amostra de validação do README
    PYTHONPATH=src python -m onfly_report \
      --input data/exemplo-validacao.csv \
      --rates data/taxas_cambio.csv \
      --output output/exemplo.json

    # relatório principal
    PYTHONPATH=src python -m onfly_report \
      --input data/reservas_hoteis.csv \
      --rates data/taxas_cambio.csv \
      --output output/report.json

### Uso de IA

Usei o Claude Code. A sessão exportada e a declaração estão em entrega/uso-de-ia/.

- **O export da sessão está no lugar errado.** O `/export` salvou o arquivo na raiz do projeto (`export_claudecode.txt`). O README pede que ele fique em `entrega/uso-de-ia/`, por exemplo como `sessao.txt`.
- **Falta a `declaracao.md`.** Ela vai em `entrega/uso-de-ia/` e deve dizer a ferramenta e o modelo usados (Claude Code, Claude Opus 5.5), o que a IA fez e o que você fez. Isso você descreve melhor do que eu.
- **O script de conferência não fica salvo.** Ele está em `/tmp/claude-1001/-home-siriusvllos-github-onfly-desafio/87bdb8b4-b896-4ee8-a496-150f3a235210/scratchpad/check.py`, uma pasta temporária. Se quiser citá-lo no README-ENTREGA como prova, copie-o para o repositório (por exemplo, `entrega/check.py`). Senão, o item 6 de "Como investiguei" vale como descrição do que foi feito.
