-- Cada id_venda é tratado como uma transação no escopo desta base.
SELECT COUNT(*) AS transacoes, ROUND(SUM(valor_total),2) AS receita,
 SUM(quantidade) AS unidades, COUNT(DISTINCT id_cliente) AS clientes,
 ROUND(SUM(valor_total)/COUNT(*),2) AS ticket_por_transacao,
 ROUND(SUM(valor_total)/SUM(quantidade),2) AS receita_por_unidade
FROM Fato_Vendas;

SELECT ano, mes, ROUND(SUM(valor_total),2) AS receita, COUNT(*) AS transacoes
FROM vw_vendas GROUP BY ano,mes ORDER BY ano,mes;

SELECT regiao, ROUND(SUM(valor_total),2) AS receita,
 ROUND(SUM(valor_total-custo_estimado),2) AS margem_bruta_estimada
FROM vw_vendas GROUP BY regiao ORDER BY receita DESC;
