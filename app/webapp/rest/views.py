# Views for boletos blueprint
from flask import abort, flash, redirect, render_template, url_for,request
from flask_login import current_user, login_required

from . import rests
from ...extensions import db
from ..models import Boleto,Share,Movement,Portfolio,Order,Follow
import json
import pandas_datareader as pdr
import datetime as dt
import requests

# Rest Views
@rests.route('/rest/order/bulk', methods=['POST'])
def add_order():
    content=request.get_json(silent=True)

    for row in content:
        print(row)
        precio_promedio=0
        for share in row['shares']:
            precio_promedio=share['price']*share['volume']+precio_promedio
        precio_promedio=precio_promedio/row['cantidad']
        add_orders(row['fecha_liquidacion'],precio_promedio,row['cantidad'],row['tipo_operacion'],row['tiker'])
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@rests.route('/rest/movimientos/bulk', methods=['POST'])
def add_movement_bulk():
    content=request.get_json(silent=True)

    for row in content:
        movement=Movement(
        fecha=row['fecha'],
        tipo_operacion=row['tipo'],
        monto=row['monto'],
        moneda=row['moneda'],
        descripcion=row['descripcion'],
        tipo_cambio=1,
        alyc_id=1)
        db.session.add(movement)
        db.session.commit()
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@rests.route('/rest/get_order/<symbol>', methods=['GET'])
def get_order(symbol):
    orders=[]
    result = db.engine.execute("select * from orders where status ='Open' and symbol='{}'".format(symbol)).fetchall()
    for row in result:
        orders.append({
        'id':row['id'],
        'buy_date' : row['buy_date'].strftime("%m/%d/%Y"),
        'type' : 'buy',
        'volume':row['volume'],
        'symbol':row['symbol'],
        'tp':row['tp'],
        'sl':row['sl'],
        'price':row['price'],
        'status':row['status'],
        'profit':0
        })
    return json.dumps(orders), 200, {'ContentType':'application/json'}

@rests.route('/rest/get_orders', methods=['GET'])
def get_orders():
    orders=[]
    result = db.engine.execute("""select * from orders where status ='open' and symbol in (SELECT symbol FROM dg_stocks.follow
    where  follow=1)""").fetchall()
    for row in result:
        orders.append({
        'id':row['id'],
        'buy_date' : row['buy_date'].strftime("%m/%d/%Y"),
        'type' : 'buy',
        'volume':row['volume'],
        'symbol':row['symbol'],
        'tp':row['tp'],
        'sl':row['sl'],
        'price':row['price'],
        'profit':0,
        'status':row['status']
        })
    return json.dumps(orders), 200, {'ContentType':'application/json'}

@rests.route('/rest/boletos/bulk', methods=['POST'])
def add_boletos_bulk():
    content=request.get_json(silent=True)
    for row in content:
        add_boleto_raw({'numero' : row['numero'],
                              'fecha_concertacion' : row['fecha_concertacion'],
                              'fecha_liquidacion':row['fecha_liquidacion'],
                              'tipo_operacion':row['tipo_operacion'],
                              'tiker':row['tiker'],
                              'cantidad':row['cantidad'],
                              'bruto':row['bruto'],
                              'arancel':row['arancel'],
                              'perc_arancel':row['perc_arancel'],
                              'mercado_importe':row['mercado_importe'],
                              'neto':row['neto'],
                              'iva':row['iva'],
                              'moneda':row['moneda'],
                              'tipo_cambio':row['tipo_cambio'],
                              'tipo_cambio_arancel':row['tipo_cambio_arancel'],
                              'interes':row['interes'],
                              'alyc_id':row['alyc_id']})
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@rests.route('/rest/follow', methods=['GET'])
def get_follow_simbol():
    orders=Follow.query.all()
    return json.dumps([i.symbol for i in orders]), 200, {'ContentType':'application/json'}

@rests.route('/rest/mapping/<symbol>', methods=['GET'])
def get_mapping(symbol):

    result = db.engine.execute("SELECT rava FROM dg_stocks.follow where follow=1 and symbol='{}' """.format(symbol)).fetchone()
    df=pdr.get_data_yahoo(result, start=dt.datetime.now() - dt.timedelta(days=7), end=dt.datetime.now()).tail(1)[['High','Low']]
    df['stock']=symbol
    df=df.reset_index()
    df.columns = df.columns.droplevel(1)
    return df.to_json(orient='records'), 200, {'ContentType':'application/json'}

@rests.route('/rest/ask_bid/<symbol>', methods=['GET'])
def get_ask_bid(symbol):

    ppi_symbol = db.engine.execute("SELECT ppi FROM dg_stocks.follow where follow=1 and symbol='{}' """.format(symbol)).fetchone()
    headers_ppi = {
        "Content-Type": "application/json",
        "AuthorizedClient": "321321321",
        "ClientKey": "pp123456",
        "Referer": "https://api.portfoliopersonal.com/Content/html/proxy.html",
        "Sec-Fetch-Mode": "cors",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }
    response=requests.get('https://api.portfoliopersonal.com/api/Cotizaciones/Item/{}/LibroOfertas/3'.format(ppi_symbol[0]), headers=headers_ppi)

    return json.dumps(response.json()['payload']), 200, {'ContentType':'application/json'}

@rests.route('/rest/intra/<symbol>', methods=['GET'])
def get_intra(symbol):

    ppi_symbol = db.engine.execute("SELECT ppi FROM dg_stocks.follow where follow=1 and symbol='{}' """.format(symbol)).fetchone()
    now=dt.datetime.now()
    hora=dt.datetime.now().hour
    week_day=dt.datetime.now().weekday()
    headers_ppi = {
        "Content-Type": "application/json",
        "AuthorizedClient": "321321321",
        "ClientKey": "pp123456",
        "Referer": "https://api.portfoliopersonal.com/Content/html/proxy.html",
        "Sec-Fetch-Mode": "cors",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    }
    response=requests.get('https://api.portfoliopersonal.com/api/Cotizaciones/Item/{}/Intradiario'.format(ppi_symbol[0]), headers=headers_ppi)

    return json.dumps(response.json()['payload']), 200, {'ContentType':'application/json'}
@rests.route('/rest/balance', methods=['GET'])
def get_balance():
    balance=db.engine.execute('''SELECT sum(monto) as monto
from dg_stocks.movements where moneda='p' ''').fetchone()['monto']
    print(balance)
    return json.dumps({'balance':float(balance)}), 200, {'ContentType':'application/json'}
