import csv
import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pipeline',ROOT/'src/pipeline.py');pipeline=importlib.util.module_from_spec(spec);spec.loader.exec_module(pipeline)

class PipelineContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.raw=Path(self.temp.name)/'raw';self.raw.mkdir();self.out=Path(self.temp.name)/'out'
        self.tables={
            'Dim_Produto.csv': [{'id_produto':1,'categoria':'A','subcategoria':'B','nome_produto':'Teste','custo':'3.00','preco':'5.00'}],
            'Dim_Regiao.csv':[{'id_regiao':1,'regiao':'Sul'}],
            'Dim_Calendario.csv':[{'data':'2024-01-01','ano':2024,'mes':1,'trimestre':1,'dia_da_semana':'Monday'}],
            'Fato_Vendas.csv':[
                {'id_venda':1,'id_produto':1,'id_cliente':7,'id_regiao':1,'data':'2024-01-01','quantidade':2,'valor_total':'10.00'},
                {'id_venda':2,'id_produto':1,'id_cliente':7,'id_regiao':1,'data':'2024-01-01','quantidade':1,'valor_total':'5.00'}]}
        self.save()
    def save(self):
        for name,rows in self.tables.items():
            with (self.raw/name).open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    def test_reconciliation_distinct_customers_and_idempotence(self):
        first=pipeline.run(self.raw,self.out);second=pipeline.run(self.raw,self.out)
        self.assertEqual(first['metrics'],second['metrics'])
        self.assertEqual(first['metrics']['receita'],15)
        self.assertEqual(first['metrics']['clientes'],1)
        self.assertEqual(first['metrics']['ticket_por_transacao'],7.5)
        self.assertEqual(first['metrics']['receita_por_unidade'],5)
        self.assertEqual(first['metrics']['margem_bruta_estimada'],6)
        with sqlite3.connect(self.out/'sales.db') as db:
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
    def test_duplicate_sale_fails_without_replacing_valid_db(self):
        pipeline.run(self.raw,self.out);before=(self.out/'sales.db').read_bytes()
        self.tables['Fato_Vendas.csv'].append(self.tables['Fato_Vendas.csv'][0].copy());self.save()
        with self.assertRaisesRegex(ValueError,'duplicada'):pipeline.run(self.raw,self.out)
        self.assertEqual(before,(self.out/'sales.db').read_bytes())
    def test_orphan_product_rejected(self):
        self.tables['Fato_Vendas.csv'][0]['id_produto']=99;self.save()
        with self.assertRaisesRegex(ValueError,'Referência'):pipeline.run(self.raw,self.out)
    def test_missing_input_is_not_an_empty_report(self):
        (self.raw/'Fato_Vendas.csv').unlink()
        with self.assertRaises(FileNotFoundError):pipeline.run(self.raw,self.out)
    def test_invalid_financial_values_rejected(self):
        for bad in ['-1','NaN','Infinity','1.234']:
            with self.subTest(bad=bad):
                self.tables['Fato_Vendas.csv'][0]['valor_total']=bad;self.save()
                with self.assertRaises(ValueError):pipeline.run(self.raw,self.out)
    def test_invalid_quantity_rejected(self):
        self.tables['Fato_Vendas.csv'][0]['quantidade']=0;self.save()
        with self.assertRaises(ValueError):pipeline.run(self.raw,self.out)

if __name__=='__main__':unittest.main()
