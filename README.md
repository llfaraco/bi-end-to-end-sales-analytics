# Sales Analytics | Modelagem de vendas e indicadores

**Projeto de estudo · SQL · Power BI · DAX**

## Problema

Como estruturar dados de vendas para acompanhar receita, quantidade vendida, desempenho de produtos, regiões e evolução no tempo?

O projeto organiza uma base de estudo e os fundamentos de um ambiente de BI. O dashboard Power BI ainda não está disponível neste repositório.

## O que está implementado

| Artefato | Conteúdo |
| --- | --- |
| `data/raw/` | CSVs de vendas, produtos, calendário e regiões |
| `sql/create_tables.sql` | Definição de tabelas com sintaxe SQLite |
| `pbix/dax_measures.txt` | Medidas de receita, quantidade, média por unidade e variação anual |
| `data/processed/`, `images/` e `pbix/` | Pastas preparadas para a evolução do projeto |

O modelo SQL prevê Fato_Vendas e dimensões de produto, cliente, região e calendário. O CSV de clientes ainda não está presente.

## Como explorar

1. Consulte os CSVs em `data/raw/`.
2. Examine a estrutura das tabelas em `sql/create_tables.sql`.
3. Para criar as tabelas em SQLite, execute a partir da raiz:
   ```bash
   sqlite3 vendas.db < sql/create_tables.sql
   ```
4. A importação dos CSVs precisa ser feita separadamente; o script cria as tabelas, mas não importa os dados.
5. Consulte `pbix/dax_measures.txt` para estudar os indicadores previstos.

## Indicadores e cuidados

- **Receita:** soma de `valor_total`.
- **Quantidade:** soma de `quantidade`.
- A medida denominada `Average Ticket` divide receita por quantidade. Ela representa **receita média por unidade**, não ticket médio por pedido.
- A variação anual requer uma dimensão calendário e relacionamentos adequadamente configurados no Power BI.

## Próximas etapas

Completar a dimensão de clientes, documentar a importação, construir o arquivo `.pbix` e publicar uma imagem do dashboard. Conclusões comerciais só devem ser registradas após a análise dos dados.

**Limite:** não há dashboard entregue, medição de impacto em empresa ou validação de execução nesta revisão.

## Contato

[Lucas Faraco](https://www.linkedin.com/in/lucasrfaraco) · [E-mail](mailto:lucas.rfaraco@gmail.com) · [Perfil e portfólio](https://github.com/llfaraco)
