# Power BI Desktop

O dashboard executável deste projeto é `artifacts/dashboard.html`. Não há `.pbix` gerado ou validado neste ambiente.

1. Execute `python src/pipeline.py` na raiz do repositório.
2. No Power BI Desktop, crie uma consulta em branco e cole `vendas.pq` no Editor Avançado. Ajuste `DataFolder` e nomeie a consulta como **Vendas**.
3. Importe `data/raw/Dim_Calendario.csv`, converta `data` para data e nomeie **Dim_Calendario**.
4. Relacione `Dim_Calendario[data]` (um) a `Vendas[data]` (muitos), com direção única. Marque o calendário como tabela de datas.
5. Crie as medidas de `pbix/dax_measures.txt`.
6. Monte cartões de receita, transações, unidades, clientes e ticket. Acrescente receita por mês, região e categoria. Use filtros de ano e região.
7. Confira os totais com `artifacts/validation.json` antes de publicar.

Os valores usam **UM**: a moeda não consta da origem. `custo_estimado` usa quantidade × custo cadastrado atual; a margem resultante não representa lucro líquido.

O modelo SQLite permanece dimensional; a exportação para Power BI está desnormalizada para facilitar a reprodução. O calendário separado permite inteligência temporal. Os arquivos M e DAX foram revisados, mas não executados no Power BI Desktop.
