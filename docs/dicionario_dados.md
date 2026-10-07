# Dicionário — base tratada (`data/processed/movimentacoes`)
| Coluna | Descrição |
|---|---|
| ano, mes, competencia | AAAAMM da movimentação |
| uf, municipio_cod | UF (sigla) e código IBGE (6 díg.) |
| cnae_secao | Seção CNAE 2.0 (A–U) |
| cbo, cbo_grande_grupo, grande_grupo_nome | CBO-2002 (6 díg.), 1º dígito e nome |
| lideranca | True se Grande Grupo 1 (dirigentes e gerentes) |
| sexo | Homem / Mulher |
| raca_cor, raca_cor_agrupada | Original e agrupada (Negra = preta+parda) |
| idade, grau_instrucao_cod, horas_contratuais, tam_estab_cod | Atributos do vínculo |
| tipo_mov, saldo | Admissão (+1) / Desligamento (−1) |
| salario | Salário de contratação/desligamento (R$), nulo se < R$ 100 |
| fora_prazo | Declaração fora do prazo (CAGEDFOR) |
Códigos originais: sexo 1=Masc, 3=Fem, 9=N/I · raça 1 Branca, 2 Preta, 3 Parda, 4 Amarela, 5 Indígena, 6 N/Inf., 9 N/Ident.
