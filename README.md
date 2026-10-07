# AV3 — Camada de Dados (Novo CAGED)

Pipeline que baixa, limpa e agrega os microdados do **Novo CAGED** (MTE/PDET) para o
projeto "Gap Salarial e Funil de Liderança". Entrega "meio caminho andado" para
frontend (Streamlit), banco e cloud.

## Fluxo
```
FTP PDET ──download──▶ data/raw/*.7z ──clean──▶ data/processed/movimentacoes/*.parquet
                                                   │
                                                   └─aggregate─▶ data/processed/agg_*.csv ──▶ Streamlit
```

## Como rodar
```bash
python -m venv .venv && source .venv/bin/activate
make install
make download      # ajuste o período no Makefile (2023-01..2024-12 por padrão)
make clean         # .7z -> parquet (processa em chunks, aguenta máquina modesta)
make aggregate     # gera os 3 CSVs leves para o app
make test
```
Fonte: `ftp://ftp.mtps.gov.br/pdet/microdados/NOVO CAGED/{ano}/{ano}{mes}/CAGEDMOV{ano}{mes}.7z`
(ver também `CAGEDFOR` = fora do prazo e `CAGEDEXC` = excluídas). Cada mês tem ~3-4 milhões
de linhas; comece com 12 meses.

## Contrato com o frontend (`src/data_access.py`)
| Função | Arquivo | Granularidade |
|---|---|---|
| `gap_salarial()` | agg_gap_salarial.csv | ano × UF × grande grupo CBO × sexo × raça: `n`, `salario_medio`, `salario_mediano` |
| `funil_lideranca()` | agg_funil_lideranca.csv | ano × UF × sexo × raça × grande grupo: `admissoes`, `pct_no_grupo_demografico` |
| `perfil_mensal()` | agg_perfil_mensal.csv | competência × UF × sexo × raça × liderança: `saldo`, `movs` |

Para migrar para banco/cloud, só altere `data_access.py` (ex.: SQL, S3, BigQuery); as páginas não mudam.

## Decisões de tratamento
- Sexo: só Homem (1) e Mulher (3); código 9 descartado. Raça: 1-6 e 9 mapeados; agrupada em
  Branca / Negra (preta+parda) / Amarela / Indígena / Não informada.
- Liderança = CBO-2002 Grande Grupo 1 (dirigentes e gerentes). CBO normalizado para 6 dígitos.
- Salário < R$ 100 vira nulo (erro de digitação); linhas mantidas para contagens.
- Salário médio calculado só sobre **admissões** (saldo = +1).

## ⚠️ Limitações metodológicas (alinhar com o grupo)
1. **O Novo CAGED não mede "tempo até liderança".** Ele registra *movimentações* (admissões e
   desligamentos), sem identificador de trabalhador nos microdados públicos e sem histórico de
   promoções. O "funil" aqui é **transversal**: % das admissões em cargos de liderança por grupo.
   Tempo de ascensão exigiria RAIS identificada ou outra fonte longitudinal; sugiro a Pessoa 3
   reformular a métrica (ex.: "razão de chance de admissão em liderança") ou usar RAIS/PNAD.
2. O salário do Novo CAGED é o **salário de contratação**, não o rendimento médio do estoque
   (esse está na RAIS). Rotule os gráficos como "salário de admissão".
3. Série começa em jan/2020; empresas têm até 12 meses para declarações fora do prazo, então
   meses recentes são revisados (use `CAGEDFOR`).
4. Valide nomes/códigos de colunas contra o layout oficial (planilha na pasta
   `NOVO CAGED` do FTP, ou https://www.gov.br/trabalho-e-emprego → PDET → Novo CAGED). O mapeamento
   está em `src/config.py` e foi testado só com dados sintéticos neste ambiente (sem acesso à rede).
