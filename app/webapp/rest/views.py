# Views for boletos blueprint
from flask import abort, flash, redirect, render_template, url_for,request
from flask_login import current_user, login_required

from . import rests
from ...extensions import db
from ..models import Boleto,Share,Movement,Portfolio,Order,Follow
import json

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
    result = db.engine.execute("""select * from orders where status ='open' and symbol in (SELECT symbol FROM follow
    where  follow=True)""").fetchall()
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
    return json.dumps([i.serialize for i in orders]), 200, {'ContentType':'application/json'}

# @rests.route('/rest/boletos/bulk', methods=['POST'])
# def add_boletos_bulk():
#     content=request.get_json(silent=True)
#     for row in content:
#         add_boleto_raw({'numero' : row['numero'],
#                               'fecha_concertacion' : row['fecha_concertacion'],
#                               'fecha_liquidacion':row['fecha_liquidacion'],
#                               'tipo_operacion':row['tipo_operacion'],
#                               'tiker':row['tiker'],
#                               'cantidad':row['cantidad'],
#                               'bruto':row['bruto'],
#                               'arancel':row['arancel'],
#                               'perc_arancel':row['perc_arancel'],
#                               'mercado_importe':row['mercado_importe'],
#                               'neto':row['neto'],
#                               'iva':row['iva'],
#                               'moneda':row['moneda'],
#                               'tipo_cambio':row['tipo_cambio'],
#                               'tipo_cambio_arancel':row['tipo_cambio_arancel'],
#                               'interes':row['interes'],
#                               'alyc_id':row['alyc_id']})
#     return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
