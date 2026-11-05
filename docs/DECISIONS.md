# Decisões de implementação

Esta evolução foi implementada com assistência de IA. As decisões abaixo descrevem o código entregue e podem ser discutidas e verificadas pelos arquivos e comandos do projeto.

## Grão e definição dos indicadores

Cada `id_venda` é único na base e representa uma transação neste exercício. O ticket divide receita por transações; a receita por unidade divide por quantidade. A versão anterior confundia as duas métricas.

## Modelo dimensional e exportação

SQLite fornece uma execução local simples, sem serviço externo. Há fato de vendas e dimensões de produto, região, data e cliente. Os IDs de clientes são extraídos da fato porque não há atributos cadastrais de cliente na origem. Não foram inventados nomes, perfil ou segmentação.

A camada `vw_vendas` gera uma exportação desnormalizada para exploração e Power BI. A fonte e o modelo dimensional permanecem separados da visualização.

## Validação antes da carga

Chaves duplicadas e referências ausentes interrompem a execução. Não se excluem registros silenciosamente. Quantidades precisam ser inteiros positivos; valores monetários precisam ser finitos e não negativos. O calendário confere ano, mês e trimestre.

A receita de entrada é somada com `Decimal`. O SQLite usa `REAL`, e o total arredondado em centavos é reconciliado com a entrada. Para sistemas financeiros operacionais, armazenamento em centavos inteiros ou tipo decimal seria preferível.

## Reexecução e falhas

A execução constrói um banco temporário e só substitui o anterior após as validações. Rodar novamente não duplica vendas. Os testes verificam que uma entrada duplicada não sobrescreve um banco válido.

Os arquivos derivados de visualização não possuem transação conjunta com o banco: uma interrupção durante a exportação pode deixar artefatos de execuções distintas. Em produção, o conjunto inteiro deveria ser publicado de forma atômica com identificador de execução.

## Margem e moeda

A base não identifica moeda. O dashboard usa UM. O custo estimado é quantidade × custo cadastrado de produto. A margem é estimada, sem impostos, frete ou histórico de custo, e não deve ser chamada de lucro líquido.

## Dashboard e Power BI

O dashboard HTML é autossuficiente e filtra os registros localmente. A lógica de totais e filtros tem teste em Node com DOM mínimo; isso não substitui testes visuais em navegadores reais.

Power Query e DAX estão disponíveis para reprodução no Desktop. Não se declara um `.pbix` ou uma execução no Power BI que não aconteceu.

## Evoluções possíveis

Para uma base maior, servir agregações em API ou em ferramenta de BI, em vez de enviar todas as linhas ao navegador. Para uso operacional, controlar moeda, mudanças de custo, permissões e procedência dos dados.
