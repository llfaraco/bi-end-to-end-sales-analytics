PRAGMA foreign_keys = ON;
CREATE TABLE Dim_Produto (
 id_produto INTEGER PRIMARY KEY, categoria TEXT NOT NULL, subcategoria TEXT NOT NULL,
 nome_produto TEXT NOT NULL, custo REAL NOT NULL CHECK(custo >= 0), preco REAL NOT NULL CHECK(preco >= 0)
);
CREATE TABLE Dim_Regiao (id_regiao INTEGER PRIMARY KEY, regiao TEXT NOT NULL);
CREATE TABLE Dim_Calendario (
 data TEXT PRIMARY KEY, ano INTEGER NOT NULL, mes INTEGER NOT NULL CHECK(mes BETWEEN 1 AND 12),
 trimestre INTEGER NOT NULL CHECK(trimestre BETWEEN 1 AND 4), dia_da_semana TEXT NOT NULL
);
-- Só há identificadores de cliente na base. Nenhum atributo pessoal foi inferido.
CREATE TABLE Dim_Cliente (id_cliente INTEGER PRIMARY KEY);
CREATE TABLE Fato_Vendas (
 id_venda INTEGER PRIMARY KEY, id_produto INTEGER NOT NULL REFERENCES Dim_Produto(id_produto),
 id_cliente INTEGER NOT NULL REFERENCES Dim_Cliente(id_cliente), id_regiao INTEGER NOT NULL REFERENCES Dim_Regiao(id_regiao),
 data TEXT NOT NULL REFERENCES Dim_Calendario(data), quantidade INTEGER NOT NULL CHECK(quantidade > 0),
 valor_total REAL NOT NULL CHECK(valor_total >= 0)
);
CREATE VIEW vw_vendas AS
 SELECT f.*, p.categoria, p.nome_produto, r.regiao, c.ano, c.mes,
 ROUND(f.quantidade * p.custo, 2) AS custo_estimado
 FROM Fato_Vendas f JOIN Dim_Produto p USING(id_produto)
 JOIN Dim_Regiao r USING(id_regiao) JOIN Dim_Calendario c USING(data);
