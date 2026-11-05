// Ajuste DataFolder para a pasta artifacts no seu computador.
let
    DataFolder = "C:\\portfolio\\bi-end-to-end-sales-analytics\\artifacts",
    Fonte = Csv.Document(File.Contents(DataFolder & "\\vendas_tratadas.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Cabecalhos = Table.PromoteHeaders(Fonte, [PromoteAllScalars=true]),
    Tipos = Table.TransformColumnTypes(Cabecalhos, {{"id_venda", Int64.Type}, {"id_produto", Int64.Type}, {"id_cliente", Int64.Type}, {"id_regiao", Int64.Type}, {"data", type date}, {"quantidade", Int64.Type}, {"valor_total", type number}, {"custo_estimado", type number}}, "en-US")
in
    Tipos
