# README-ENTREGA — Desafio Onfly de Consolidador de reservas de hotel

## Resumo
O CLI gerava números errados e não passava nos testes por causa de quatro erros mais simples no código fonte; além disso, havia um defeito adicional que impactaria no relatório gerado a partir do arquivo `data/reservas_hoteis.csv`.

Ao corrigir os quatro primeiros erros, os 5 testes originais (que não foram alterados) começaram a passar um a um. Para maior confiabilidade, foram adicionados 9 outros testes, e no estado do código da entrega final, todos os 14 testes são concluídos com sucesso.

Além dos testes, a execução do script sobre o arquivo `data/exemplo-validacao.csv` bate com o resultado disponibilizado na seção **Amostra de validação** do arquivo `./README.md`, e a execução sobre o arquivo de reservas foi conferida com um cálculo independente (etapa 7 de "Como investiguei").

A partir desses pontos, eu cheguei à conclusão de que o código tinha sido efetivamente corrigido, e o desafio concluído.

## Índice

Esse documento inclui as seguintes seções:
* **Defeitos corrigidos** -> faz uma descrição dos defeitos identificados, em quais arquivos, por qual motivo/causa e quais são os testes correlatos (sejam originais ou adicionados por mim)
    * _Correções aplicadas:_ explica o que foi modificado em cada arquivo
    * _Testes adicionados:_ descreve o que cada teste novo verifica
* **Como investiguei/abordei o problema** -> descreve minha experiência com as ferramentas do desafio e as etapas que segui, do ambiente local à conferência do relatório principal
    * _1. Ambiente local:_ criação do ambiente com Python 3.11 e instalação das dependências
    * _2. Execução do CLI:_ os primeiros sinais de erro nos arquivos de reservas e de exemplo
    * _3. Mapeamento do código:_ onde cada etapa do processamento acontece em `src/onfly_report`
    * _4. Comparação com as regras de negócio:_ como os cinco defeitos foram identificados e ligados aos testes
    * _5. Correções incrementais:_ uma correção por vez, com testes e commit isolado
    * _6. Amostra de validação:_ conferência com as tabelas do `./README.md`
    * _7. Relatório principal:_ conferência com um cálculo independente
* **Como validar** -> comandos para criar o ambiente, rodar os testes e gerar os dois relatórios (amostra e principal)
* **Resultado do pytest** -> saída dos testes antes e depois das correções
* **Uso de IA** -> onde estão a sessão exportada e a declaração de uso

## Defeitos corrigidos

| # | Defeito | Arquivo | Causa raiz | Testes |
|-|-|-|-|-|
| 1 | Conversão de câmbio errada | `services/currency_converter.py` | O valor (`amount`) estava sendo dividido pela taxa (`rates[currency]`) ao invés de multiplicado, e passado por `float` ao invés de `Decimal`. | `test_currency*.py` |
| 2 | Cálculo de noites errado | `services/stay_calculator.py` | O cálculo só funcionaria para dias no mesmo mês, por ignorar a diferença real entre as datas, que poderia variar entre mês e ano. | `test_nights*.py` |
| 3 | `NO_SHOW` contado como faturável | `services/status_policy.py` | Estavam passando quaisquer `status != "CANCELLED"`, o que incluía `NO_SHOW`, mesmo que as regras de negócio colocassem só `CONFIRMED` como faturável. | `test_status_rules.py` |
| 4 | Ranking de hotéis em ordem crescente | `services/report_builder.py` | A chave de ordenação (`amount, hotel_id`) ordenava o valor em ordem crescente ao invés do certo: ordem do maior para o menor, e com desempate por `hotel_id` crescente. | `test_top_hotels*.py` |
| 5 | Leitura do arquivo parava em 200 linhas | `repositories/csv_reservation_repository.py` | Existia um trecho de código `if len(rows) == 200: break` que descartava todas as reservas do CSV a partir da 201ª. | `test_reads_all_rows.py` |

### Correções aplicadas

1. `services/currency_converter.py`
```diff
- return Decimal(str(float(amount) / float(rate)))
+ return amount * rates[currency]
```
Multiplica pela taxa, como definido nas regras de negócio. O valor e a taxa já são `Decimal`, então não é preciso fazer nenhuma das conversões de tipo que estava sendo feita.

2. `services/stay_calculator.py`
```diff
- return (checkout.day - checkin.day) * rooms
+ return (checkout - checkin).days * rooms
```
A subtração `checkout - checkin` retorna um intervalo de tempo com a diferença real em dias, atravessando mês e ano. O `.day` é só o dia do mês (1 a 31).

3. `services/status_policy.py`
```diff
- return status != "CANCELLED"
+ return status == "CONFIRMED"
```
Garante que só `CONFIRMED` fatura, e além de excluir `NO_SHOW`, qualquer status inesperado ou adicionado posteriormente também fica fora do faturamento.

4. `services/report_builder.py`
```diff
- key=lambda item: (item[1]["amount"], item[0])
+ key=lambda item: (-item[1]["amount"], item[0])
```
Nega o total, deixando-o em ordem decrescente, e mantém o desempate por `hotel_id` em ordem crescente.

5. `repositories/csv_reservation_repository.py`
```diff
- rows: list[RawRow] = []
- for values in reader:
-     rows.append(RawRow(line_number=reader.line_num, values=values))
-     if len(rows) == 200:
-         break
- return rows
+ return [RawRow(line_number=reader.line_num, values=values) for values in reader]
```
Continua lendo até o fim do arquivo, ao invés de parar (fazer um `break`) ao completar 200 reservas.

### Testes adicionados

| Arquivo | Teste executado |
|-|-|
| `tests/test_currency_eur.py` | EUR p/ BRL multiplicando pela taxa (ex: 150 × 5,88 = 882,00); produto exato em `Decimal`, que falharia com `float` (ex: 19,99 × 5,88 = 117,5412); conversão de EUR somada a BRL no relatório completo (`335,0824 → 335.08`) |
| `tests/test_nights_year_boundary.py` | Virada de ano: 30/12/2024 - 02/01/2025 com 2 quartos = 6 noites; by_month usa o mês do check-in (2024-12) |
| `tests/test_top_hotels_tiebreak.py` | Desempate por hotel_id crescente; empate exato após conversão (100 USD = 542 BRL) |
| `tests/test_reads_all_rows.py` | Leitura de mais de 200 linhas; reserva na linha 201 entra na contagem |

## Como investiguei/abordei o problema

Em relação à minha experiência com o desafio, eu percebi que ele veio com uma mistura de ferramentas que eu conheço bem e acho que sei usar bem (como Python, Conda, pyenv, pip, git e, já que foi permitido, Claude Code) e coisas que eu usei muito pouco, e muito superficialmente (a variável de ambiente `PYTHONPATH`, e pytest). Essas últimas foram muito bem definidas no `./README.md`, então foram bem manejáveis.

Sobre a resolução do problema concretamente, as etapas que tomei foram:

1. **Clonei o repositório e defini o ambiente local ->** Criei e ativei um ambiente isolado com Python 3.11 utilizando o Conda (`conda create -n py311 python=3.11 -y` e `conda activate py311`), depois a `.venv` na qual instalei as dependências do `requirements-dev.txt`.

    _OBS: usei o Conda porque meu sistema é o Ubuntu 20.04 (Focal Fossa), que não tem mais suporte do PPA Deadsnakes. A instalação do `python3.11` pelo `apt` falhava com um erro sobre o pacote, e não sobre o PPA, o que dificultou entender a causa._

2. **Rodei o CLI buscando mapear os erros ->** Primeiro eu executei o CLI sobre o arquivo principal (`data/reservas_hoteis.csv`), e percebi algumas coisas no resultado que não faziam sentido:
    * Apareciam noites negativas, tanto no total quanto em vários meses e hotéis;
    * A média por noite estava zerada (e lendo as regras de negócio, imaginei que por causa do total de noites negativo);
    * Só tinham 200 reservas contadas, mas 300 linhas no arquivo. De início imaginei que fosse por causa da regra de negócio de contar somente `CONFIRMED`, mas depois vi que não era isso: `total_reservations` conta todas as reservas, independente do status (a causa real aparece na etapa 4).

    O `./README.md` não trazia o resultado esperado pra esse arquivo, então registrei que tinha algo de errado na execução, e que podia ou não ser o mesmo erro que fazia os testes falharem.

    Depois passei pro próximo arquivo, rodei o CLI sobre `data/exemplo-validacao.csv`, e constatei que realmente vinha tudo errado: noites negativas, total abaixo do esperado, e uma reserva `NO_SHOW` aparecendo no ranking.

3. **Mapeei o código ->** Tendo constatado o erro mas não sabendo em qual parte do código em `./src/onfly_report` ele estava, coloquei o Claude Code para localizar cada etapa de processamento descrita (ler → converter tipos → contar status → filtrar CONFIRMED → agregar).

    Descobri que: `ReportBuilder.build()` orquestra tudo, os repositórios leem os CSVs, o `RowParser` converte os tipos e os módulos de `services/` cuidam de status, noites e câmbio. Ficou claro que o código estava bem modularizado, e que cada regra do README aponta para uma função só.

    Nessa mesma resposta, o Claude avisou que havia localizado algumas incongruências em relação às regras de negócio e aos códigos, e eu pedi que ele as enumerasse.

4. **Comparei as funções com as regras de negócio ->** Nesta etapa, o Claude me retornou as análises que definiram os cinco erros descritos acima:
    * Listou a divisão em vez de multiplicação no câmbio, o `.day` em vez da diferença entre datas, o `!= "CANCELLED"` em vez de `== "CONFIRMED"` e a ordenação crescente no ranking.
    * Ligou cada falha do teste a um defeito. Por exemplo, `'118.45' == '642.00'` corresponde a 100 + 100 / 5,42 em vez de 100 + 100 × 5,42, e `-28 == 3` corresponde a 2 − 30 (dia do check-out menos dia do check-in). Uma dessas ligações, para o teste `test_currency_conversion_to_brl`, estava imprecisa: a falha foi atribuída à divisão e ao uso de `float` em vez de `Decimal`, mas apenas a correção da operação já resolvia. O `float` é um defeito real, mas nenhum teste fornecido o pegava; o teste de `Decimal` vs `float` em `test_currency_eur.py` cobre justamente isso.
    * Citou um defeito que não seria percebido pelos testes, isso é, o `break` que interrompia a leitura em 200 linhas. Ele não afeta nenhum teste, tendo em vista o tamanho da amostra (12 linhas), mas explicava as 200 reservas exatas que vi no passo 2.

5. **Executei correções incrementais ->** Conduzi as correções uma a uma: decidia o que corrigir e se haveria teste novo, o Claude aplicava (as correções eram simples o suficiente para isso), e eu rodava `pytest -q` e conferia antes de seguir. Depois de corrigidos, eu testava fora da sessão com CSVs pequenos e intencionalmente certos/errados, rodava o CLI direto com `PYTHONPATH=src python -m onfly_report` e comparava a saída com o resultado esperado. Assim que eu aceitava que um problema estivesse corrigido, eu fazia um commit isolado e passava pro próximo.

6. **Rodei a amostra de validação ->** Com as correções, o CLI sobre `data/exemplo-validacao.csv` passou a bater com todas as tabelas do `./README.md`, e eu dei tudo por corrigido, exceto a questão das 200 linhas.

7. **Conferi o relatório principal ->** Como o README não traz o resultado esperado para `data/reservas_hoteis.csv`, eu pedi ao Claude Code para recalcular o relatório com um script separado, que eu pudesse comparar com o gerado pelo CLI. O resultado bateu em todos os campos, exceto `generated_at`. Esse script também confirmou que os dados não tinham "armadilhas" (IDs repetidos, hotéis com nomes diferentes, espaços sobrando ou status e moedas desconhecidos), o que deu confiança de que o relatório principal está correto.

_OBS: Os CSVs rascunho citados na etapa 5 e o script citado na 7 não foram adicionados à entrega, mas qualquer dúvida sigo à disposição._

## Como validar

```bash
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
```

## Resultado do pytest

Antes das correções (só os testes fornecidos):

```
FAILED tests/test_currency.py::test_currency_conversion_to_brl - AssertionError: assert '118.45' == '642.00'
FAILED tests/test_nights.py::test_nights_across_month_boundary - assert -28 == 3
FAILED tests/test_regression_report.py::test_regression_report_on_sample - AssertionError: assert {'average_nig...ions': 0, ...} == {'average_nig...ions': 0, ...}
FAILED tests/test_status_rules.py::test_status_rules_exclude_cancelled_and_no_show - AssertionError: assert '120.00' == '100.00'
FAILED tests/test_top_hotels.py::test_top_hotels_are_ranked_descending - AssertionError: assert ['H04', 'H03', 'H02'] == ['H01', 'H02', 'H03']
5 failed in 0.37s
```

Depois das correções (5 fornecidos + 9 adicionados), com Python 3.11:

```
..............                                                           [100%]
14 passed in 0.81s
```

## Uso de IA

Usei o Claude Code. A sessão exportada e a declaração estão em `entrega/uso-de-ia/`.
