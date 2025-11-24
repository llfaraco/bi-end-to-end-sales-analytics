-- SQL script to create tables (SQLite syntax) and load from CSV
-- Adjust paths if necessary

CREATE TABLE IF NOT EXISTS Dim_Produto (
  id_produto INTEGER PRIMARY KEY,
  categoria TEXT,
  subcategoria TEXT,
  nome_produto TEXT,
  custo NUMERIC,
  preco NUMERIC
);

CREATE TABLE IF NOT EXISTS Dim_Cliente (
  id_cliente INTEGER PRIMARY KEY,
  nome_cliente TEXT,
  sexo TEXT,
  faixa_etaria TEXT,
  tipo_cliente TEXT,
  cidade TEXT,
  estado TEXT,
  id_regiao INTEGER
);

CREATE TABLE IF NOT EXISTS Dim_Regiao (
  id_regiao INTEGER PRIMARY KEY,
  regiao TEXT
);

CREATE TABLE IF NOT EXISTS Dim_Calendario (
  data TEXT PRIMARY KEY,
  ano INTEGER,
  mes INTEGER,
  trimestre INTEGER,
  dia_da_semana TEXT
);

CREATE TABLE IF NOT EXISTS Fato_Vendas (
  id_venda INTEGER PRIMARY KEY,
  id_produto INTEGER,
  id_cliente INTEGER,
  id_regiao INTEGER,
  data TEXT,
  quantidade INTEGER,
  valor_total NUMERIC
);
