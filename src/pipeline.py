"""CSV -> validação -> SQLite -> agregações -> dashboard. Apenas biblioteca padrão."""
import argparse
import csv
import hashlib
import json
import sqlite3
import tempfile
import time
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = {
 'Dim_Produto': ['id_produto','categoria','subcategoria','nome_produto','custo','preco'],
 'Dim_Regiao': ['id_regiao','regiao'],
 'Dim_Calendario': ['data','ano','mes','trimestre','dia_da_semana'],
 'Fato_Vendas': ['id_venda','id_produto','id_cliente','id_regiao','data','quantidade','valor_total'],
}
FILES = [name+'.csv' for name in SCHEMA]


def read_rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def positive_int(value, name, allow_zero=False):
    try:
        parsed = int(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f'{name}: inteiro inválido: {value!r}') from exc
    if str(parsed) != str(value).strip() or parsed < (0 if allow_zero else 1):
        raise ValueError(f'{name}: inteiro fora do domínio: {value!r}')
    return parsed


def money(value, name):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError) as exc:
        raise ValueError(f'{name}: valor monetário inválido') from exc
    if not amount.is_finite() or amount < 0 or amount != amount.quantize(Decimal('.01')):
        raise ValueError(f'{name}: valor deve ser finito, não negativo e ter até 2 casas')
    return amount


def unique(rows, key):
    seen = set()
    for row in rows:
        value = row[key]
        if value in seen:
            raise ValueError(f'Chave duplicada: {key}={value}')
        seen.add(value)
    return seen


def prepare(raw):
    tables = {name[:-4]: read_rows(raw / name) for name in FILES}
    for table, columns in SCHEMA.items():
        for row in tables[table]:
            if set(row) != set(columns) or any(row[c] is None for c in columns):
                raise ValueError(f'Esquema inválido: {table}')
    for table, key in [('Dim_Produto','id_produto'),('Dim_Regiao','id_regiao'),('Dim_Calendario','data'),('Fato_Vendas','id_venda')]:
        if not tables[table]:
            raise ValueError(f'Tabela vazia: {table}')
        unique(tables[table], key)
    products = {positive_int(r['id_produto'],'id_produto') for r in tables['Dim_Produto']}
    regions = {positive_int(r['id_regiao'],'id_regiao') for r in tables['Dim_Regiao']}
    dates = {date.fromisoformat(r['data']).isoformat() for r in tables['Dim_Calendario']}
    for r in tables['Dim_Calendario']:
        parsed = date.fromisoformat(r['data'])
        if (int(r['ano']),int(r['mes']),int(r['trimestre'])) != (parsed.year,parsed.month,(parsed.month-1)//3+1):
            raise ValueError('Calendário inconsistente')
    for r in tables['Dim_Produto']:
        money(r['custo'],'custo'); money(r['preco'],'preco')
        if not all(r[k].strip() for k in ['categoria','subcategoria','nome_produto']):
            raise ValueError('Produto com atributo vazio')
    for r in tables['Dim_Regiao']:
        if not r['regiao'].strip():
            raise ValueError('Região vazia')
    total = Decimal('0')
    clients = set()
    for r in tables['Fato_Vendas']:
        positive_int(r['id_venda'],'id_venda')
        pid = positive_int(r['id_produto'],'id_produto')
        rid = positive_int(r['id_regiao'],'id_regiao')
        clients.add(positive_int(r['id_cliente'],'id_cliente'))
        positive_int(r['quantidade'],'quantidade')
        total += money(r['valor_total'],'valor_total')
        if pid not in products or rid not in regions or r['data'] not in dates:
            raise ValueError(f'Referência ausente na venda {r["id_venda"]}')
    tables['Dim_Cliente'] = [{'id_cliente': c} for c in sorted(clients)]
    return tables, total


def load_db(db, tables):
    db.executescript((ROOT/'sql/create_tables.sql').read_text())
    for name in ['Dim_Produto','Dim_Regiao','Dim_Calendario','Dim_Cliente','Fato_Vendas']:
        rows = tables[name]
        columns = list(rows[0])
        values = [tuple(r[c] for c in columns) for r in rows]
        db.executemany(f'INSERT INTO {name} ({",".join(columns)}) VALUES ({",".join("?" for _ in columns)})', values)
    db.commit()
    if db.execute('PRAGMA foreign_key_check').fetchall():
        raise ValueError('Falha na integridade referencial')


def report(db):
    revenue, transactions, units, customers, costs = db.execute('SELECT SUM(valor_total), COUNT(*), SUM(quantidade), COUNT(DISTINCT id_cliente), SUM(custo_estimado) FROM vw_vendas').fetchone()
    return dict(receita=round(revenue,2), transacoes=transactions, unidades=units, clientes=customers,
                ticket_por_transacao=round(revenue/transactions,2), receita_por_unidade=round(revenue/units,2),
                custo_estimado=round(costs,2), margem_bruta_estimada=round(revenue-costs,2))


def export_csv(db, sql, target):
    cur = db.execute(sql)
    with target.open('w',encoding='utf-8',newline='') as stream:
        writer = csv.writer(stream); writer.writerow([c[0] for c in cur.description]); writer.writerows(cur)


def dashboard(data, metrics):
    payload = json.dumps(data,ensure_ascii=False).replace('<','\\u003c')
    template = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sales Analytics | Lucas Faraco</title>
<style>body{font:16px system-ui;background:#f1f5f9;color:#172b40;margin:0}main{max-width:1120px;margin:auto;padding:28px}h1{margin-bottom:4px}p{line-height:1.6}.sub{color:#475569}.filters,.cards{display:flex;gap:14px;flex-wrap:wrap;margin:22px 0}select{font:inherit;padding:9px;background:white;border:1px solid #94a3b8;border-radius:6px}.card,section{background:white;border-radius:10px;padding:20px;box-shadow:0 1px 4px #cbd5e1}.card{flex:1;min-width:150px}.card strong{display:block;font-size:25px;margin-top:8px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}section{margin:10px 0}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:8px;border-bottom:1px solid #e2e8f0}.bar{height:14px;background:#5266cc;border-radius:3px;display:block;margin:4px 0}.tablewrap{overflow-x:auto}footer{font-size:13px;color:#475569;margin:20px 0}@media(max-width:720px){main{padding:16px}.grid{grid-template-columns:1fr}.card{min-width:125px}h1{font-size:25px}}</style>
<main><h1>Sales Analytics</h1><p class="sub">Receita, volume e desempenho comercial | Portfólio de Lucas Faraco</p><p>Base de estudo, sem empresa identificada. A moeda não consta da origem; valores são apresentados em <strong>unidades monetárias (UM)</strong>.</p>
<div class="filters"><label>Ano <select id="year" aria-label="Filtrar por ano"></select></label><label>Região <select id="region" aria-label="Filtrar por região"></select></label></div>
<div class="cards" id="cards" aria-live="polite"></div><div class="grid"><section><h2>Receita mensal</h2><div id="months"></div></section><section><h2>Receita por categoria</h2><div id="categories"></div></section></div><section><h2>Receita por região</h2><div id="regions"></div></section>
<footer>Grão: uma linha por id_venda, tratado como transação. Ticket = receita ÷ transações. Margem bruta estimada usa o custo cadastrado atual, sem impostos, frete ou histórico de custos. Clientes distintos são apurados no filtro atual. Nenhum dado de usuário real é carregado. Fonte: CSVs deste repositório.</footer></main>
<script>
const data=PAYLOAD;const money=v=>new Intl.NumberFormat('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(v)+' UM';const integer=v=>new Intl.NumberFormat('pt-BR').format(v);const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const yrs=[...new Set(data.map(r=>r.data.slice(0,4)))].sort();const regs=[...new Set(data.map(r=>r.regiao))].sort();
for(const [id,vals] of [['year',yrs],['region',regs]]){document.getElementById(id).innerHTML='<option value="">Todos</option>'+vals.map(v=>'<option value="'+esc(v)+'">'+esc(v)+'</option>').join('');document.getElementById(id).addEventListener('change',render)}
function grouped(rows,key){const groups={};for(const r of rows){const k=key(r);groups[k]=(groups[k]||0)+r.valor_total}return Object.entries(groups)}
function bars(id,items,sort){if(sort)items.sort((a,b)=>b[1]-a[1]);else items.sort((a,b)=>a[0].localeCompare(b[0]));const max=Math.max(1,...items.map(x=>x[1]));document.getElementById(id).innerHTML='<div class="tablewrap"><table><thead><tr><th>Grupo</th><th>Receita</th></tr></thead><tbody>'+items.map(([label,v])=>'<tr><td>'+esc(label)+'<span class="bar" style="width:'+Math.max(1,v/max*100)+'%"></span></td><td>'+money(v)+'</td></tr>').join('')+'</tbody></table></div>'}
function render(){const y=document.getElementById('year').value,region=document.getElementById('region').value;const rows=data.filter(r=>(!y||r.data.startsWith(y))&&(!region||r.regiao===region));const sum=k=>rows.reduce((s,r)=>s+r[k],0);const revenue=sum('valor_total'),count=rows.length,units=sum('quantidade');const metrics=[['Receita',money(revenue)],['Transações',integer(count)],['Unidades',integer(units)],['Clientes distintos',integer(new Set(rows.map(r=>r.id_cliente)).size)],['Ticket por transação',count?money(revenue/count):'Sem dados'],['Margem estimada',money(revenue-sum('custo_estimado'))]];document.getElementById('cards').innerHTML=metrics.map(([k,v])=>'<div class="card">'+k+'<strong>'+v+'</strong></div>').join('');bars('months',grouped(rows,r=>r.data.slice(0,7)),false);bars('categories',grouped(rows,r=>r.categoria),true);bars('regions',grouped(rows,r=>r.regiao),true)}render();
</script></html>'''
    return template.replace('PAYLOAD',payload)


def run(raw=ROOT/'data/raw', output=ROOT/'artifacts'):
    start = time.perf_counter()
    tables, expected = prepare(Path(raw))
    output = Path(output); output.mkdir(parents=True,exist_ok=True)
    # Constrói em temporário: uma falha não substitui o banco válido anterior.
    with tempfile.TemporaryDirectory(dir=output) as temp:
        staging = Path(temp)/'sales.db'
        with sqlite3.connect(staging) as db:
            db.row_factory = sqlite3.Row
            load_db(db,tables)
            measured = report(db)
            if abs(Decimal(str(measured['receita']))-expected) > Decimal('.005'):
                raise ValueError('Receita SQL não reconcilia com a entrada')
            export_csv(db,'SELECT * FROM vw_vendas ORDER BY id_venda',output/'vendas_tratadas.csv')
            export_csv(db,'SELECT ano,mes,ROUND(SUM(valor_total),2) receita,COUNT(*) transacoes FROM vw_vendas GROUP BY ano,mes ORDER BY ano,mes',output/'receita_mensal.csv')
            rows = [dict(r) for r in db.execute('SELECT id_cliente,data,quantidade,valor_total,categoria,regiao,custo_estimado FROM vw_vendas ORDER BY id_venda')]
            (output/'dashboard.html').write_text(dashboard(rows,measured),encoding='utf-8')
        staging.replace(output/'sales.db')
    audit = dict(generated_at=datetime.now(timezone.utc).isoformat(), duration_seconds=round(time.perf_counter()-start,4),
                 python=__import__('platform').python_version(), input_sha256={f:hashlib.sha256((Path(raw)/f).read_bytes()).hexdigest() for f in FILES},
                 checks={'unique_keys':True,'valid_domains':True,'foreign_keys':True,'revenue_reconciled':True}, metrics=measured,
                 period={'start':min(r['data'] for r in tables['Fato_Vendas']),'end':max(r['data'] for r in tables['Fato_Vendas'])},
                 assumptions=['Base de estudo; origem e moeda não documentadas nos arquivos recebidos.','id_venda tratado como uma transação; id_cliente é identificador sem atributos inferidos.','Custo estimado usa custo cadastrado, sem impostos, frete ou variação histórica.'])
    (output/'validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(audit,ensure_ascii=False,indent=2))
    return audit

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--raw',type=Path,default=ROOT/'data/raw');parser.add_argument('--output',type=Path,default=ROOT/'artifacts')
    args=parser.parse_args();run(args.raw,args.output)
