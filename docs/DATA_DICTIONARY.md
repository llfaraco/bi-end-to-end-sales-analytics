# Dicionário e origem

Os CSVs já estavam no repositório. A origem, o método de geração e a licença específica da base não estão documentados. Este material é apresentado como base de estudo, sem atribuição a uma empresa real ou uso de dados comerciais reais.

| Campo | Significado no projeto |
| --- | --- |
| id_venda | Identificador único; uma transação no escopo do exercício |
| id_cliente | Identificador; dimensão derivada sem atributos adicionais |
| id_produto | Referência ao cadastro de produtos |
| id_regiao | Referência ao cadastro de regiões |
| data | Data ISO, com correspondência no calendário |
| quantidade | Número inteiro positivo de unidades |
| valor_total | Receita da linha em UM, não negativa |
| custo | Custo unitário cadastrado; sem histórico temporal |
| preco | Preço cadastrado; não substitui o valor efetivamente registrado na venda |
| custo_estimado | quantidade × custo; arredondado em centavos |

O pipeline não força `valor_total = quantidade × preco`, pois a base não documenta descontos e o preço cadastrado não garante preço de transação. Também não infere dados pessoais a partir do ID do cliente.
