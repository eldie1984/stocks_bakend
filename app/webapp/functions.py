from sqlalchemy import func
import json

from ..extensions import db
from .models import Boleto,Share,Movement,Portfolio,Order,Follow

def add_stock(data):
    """
    Add a ticker to the database
    """
    precio_promedio=0
    for share in data['shares']:
        ticker = Share(tiker=data['symbol'],
                                type=data['tipo_operacion'],
                                quantity=share['volume'],
                                price = share['price'],
                                date = data['fecha_concertacion'],
                                boleto_id = data['boleto_id'],
                                dolar = 0)
        #TODO : change dolar for exchange shange quantitu for volume
        precio_promedio=share['price']*share['volume']+precio_promedio
        db.session.add(ticker)
        db.session.commit()
    precio_promedio=precio_promedio/data['cantidad']
    add_orders(data['fecha_concertacion'],precio_promedio,data['cantidad'],data['tipo_operacion'],data['symbol'],tp=0,sl=0)


def add_boleto_raw(data):
    if data['tipo_operacion'] != 'acc':
        boleto = Boleto(numero = data['numero'],
                        fecha_concertacion = data['fecha_concertacion'],
                        fecha_liquidacion=data['fecha_liquidacion'],
                        tipo_operacion=data['tipo_operacion'],
                        tiker=data['symbol'],
                        cantidad=data['cantidad'],
                        bruto=data['bruto'],
                        arancel=data['arancel'],
                        perc_arancel=data['perc_arancel'],
                        mercado_importe=data['mercado_importe'],
                        neto=data['neto'],
                        iva=data['iva'],
                        moneda=data['moneda'],
                        tipo_cambio=data['tipo_cambio'],
                        tipo_cambio_arancel=data['tipo_cambio_arancel'],
                        interes=data['interes'],
                        alyc_id=data['alyc_id'])
        db.session.add(boleto)
        db.session.commit()
        data['boleto_id']=boleto.id
    else:
        boleto_acc = Boleto(numero = data['numero'],
                        fecha_concertacion = data['fecha_concertacion'],
                        fecha_liquidacion=data['fecha_concertacion'],
                        tipo_operacion='acc',
                        bruto=data['bruto'],
                        arancel=0,
                        perc_arancel=0,
                        mercado_importe=0,
                        neto=data['bruto'],
                        iva=data['iva'],
                        moneda=data['moneda'],
                        alyc_id=data['alyc_id'])
        boleto_acf = Boleto(numero = data['numero']+1,
                        fecha_concertacion = data['fecha_concertacion'],
                        fecha_liquidacion=data['fecha_liquidacion'],
                        tipo_operacion='acf',
                        bruto=data['bruto'],
                        arancel=data['arancel'],
                        perc_arancel=data['perc_arancel'],
                        mercado_importe=data['mercado_importe'],
                        neto=data['neto'],
                        iva=data['iva'],
                        moneda=data['moneda'],
                        interes=data['interes'],
                        alyc_id=data['alyc_id'])
        db.session.add(boleto_acc)
        db.session.add(boleto_acf)
        db.session.commit()
        data['boleto_acc']=boleto_acc.id
        data['boleto_acf']=boleto_acf.id
    print('agregue el boleto')

    add_movement_raw(data)
    if data['tipo_operacion']=='vc' or data['tipo_operacion']=='cc':
        print('voy a shares')
        add_stock(data)

def add_movement_raw(data):
    if  data['tipo_operacion']=='vc' :
        print('Agregue movimietno venta')
        movement=Movement(boleto_nro=data['boleto_id'],
        fecha=data['fecha_concertacion'],
        tipo_operacion=data['tipo_operacion'],
        monto=data['neto'],
        moneda=data['moneda'],
        tipo_cambio=data['tipo_cambio'],
        descripcion='Boleto / {} / VENTA / 2 / {} / PESOS'.format(data['numero'],data['symbol']),
        alyc_id=data['alyc_id'])
        db.session.add(movement)
    elif  data['tipo_operacion']=='acc':
        print('Agregue movimietno acf')
        print(data)
        movement_acf=Movement(boleto_nro=data['boleto_acf'],
        fecha=data['fecha_liquidacion'],
        tipo_operacion='acf',
        monto=data['neto'],
        moneda=data['moneda'],
        tipo_cambio=data['tipo_cambio'],
        descripcion='Boleto / {} / APCOLFUT / 2 / {} / PESOS'.format(data['numero']+1),
        alyc_id=data['alyc_id'])
        print('Agregue movimietno apertura colocadora contado')
        movement_acc=Movement(boleto_nro=data['boleto_acc'],
        fecha=data['fecha_concertacion'],
        tipo_operacion='acc',
        monto=-data['bruto'],
        moneda=data['moneda'],
        tipo_cambio=data['tipo_cambio'],
        descripcion='Boleto / {} / APCOLCONT / 0 / PESOS'.format(data['numero']),
        alyc_id=data['alyc_id'])
        db.session.add(movement_acf)
        db.session.add(movement_acc)
    elif  data['tipo_operacion']=='cc':
        print('Agregue movimietno compra ')
        movement=Movement(boleto_nro=data['boleto_id'],
        fecha=data['fecha_concertacion'],
        tipo_operacion=data['tipo_operacion'],
        monto=-data['neto'],
        moneda=data['moneda'],
        tipo_cambio=data['tipo_cambio'],
        descripcion='Boleto / {} / COMPRA / 2 / {} / PESOS'.format(data['numero'],data['symbol']),
        alyc_id=data['alyc_id'])

        db.session.add(movement)
    db.session.commit()

def add_orders(action_date,price,volume,type,symbol,tp=0,sl=0):
    result = db.engine.execute("select * from orders where sell_date is null and symbol='{}'".format(symbol)).fetchone()
    if result:
        order = Order.query.get_or_404(result['id'])
    if result:
        if type=='vc':
            order.sell_price=price
            order.sell_date=action_date
            if order.volume > volume:
                order2=Order(
                buy_date = order.buy_date,
                type = 'buy',
                volume=order.volume-volume,
                symbol=order.symbol,
                tp=order.tp,
                sl=order.sl,
                price=order.price,
                status='open')
                order.volume=volume
                db.session.add(order2)
            order.status='close'
            order.profit_amount=volume*(price-order.price)

        elif type=='cc':
            order.price=(order.volume * order.price+volume*price)/(order.volume+volume)
            order.volume=order.volume+volume
        elif type=='div':
            order.price=(order.volume * order.price)/(order.volume+volume)
            order.volume=order.volume+volume
    else:
        order=Order(
        buy_date = action_date,
        type = 'buy',
        volume=volume,
        symbol=symbol,
        tp=tp,
        sl=sl,
        price=price,
        status='open')
    db.session.add(order)
    db.session.commit()
