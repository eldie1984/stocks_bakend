# Views for boletos blueprint
from flask import abort, flash, redirect, render_template, url_for,request
from flask_login import current_user, login_required
from sqlalchemy import func
import json

from . import boletos
from .forms import BoletosForm,TickerForm
from ...extensions import db
from ..models import Boleto,Share,Movement,Portfolio,Order

# Boleto Views


@boletos.route('/boletos', methods=['GET', 'POST'])
@login_required
def list_boletos():
    """
    List all boletos
    """


    boletos = Boleto.query.order_by(Boleto.fecha_concertacion.desc()).all()

    return render_template('boletos/boletos.html',
                           boletos=boletos, title="Boletos")


@boletos.route('/boletos/add', methods=['GET', 'POST'])
@login_required
def add_boleto():
    """
    Add a boletos to the database
    """


    add_boleto = True

    form = BoletosForm()
    if form.validate_on_submit():

        # boleto = Boleto(numero = form.numero.data,
        #                 fecha_concertacion = form.fecha_concertacion.data,
        #                 fecha_liquidacion=form.fecha_liquidacion.data,
        #                 tipo_operacion=form.tipo_operacion.data,
        #                 tiker=form.tiker.data,
        #                 cantidad=form.cantidad.data,
        #                 bruto=form.bruto.data,
        #                 arancel=form.arancel.data,
        #                 perc_arancel=form.perc_arancel.data,
        #                 mercado_importe=form.mercado_importe.data,
        #                 neto=form.neto.data,
        #                 iva=form.iva.data,
        #                 moneda=form.moneda.data,
        #                 tipo_cambio=form.tipo_cambio.data,
        #                 tipo_cambio_arancel=form.tipo_cambio_arancel.data,
        #                 alyc_id=form.alyc_id.data.id)
        #
        # if  form.tipo_operacion.data=='vc' or form.tipo_operacion.data=='acf':
        #     movement=Movement(boleto_nro=boleto.id,
        #     fecha=boleto.fecha_concertacion,
        #     tipo_operacion=boleto.tipo_operacion,
        #     monto=boleto.neto,
        #     tipo_cambio=boleto.tipo_cambio,
        #     alyc_id=boleto.alyc_id)
        # elif  form.tipo_operacion.data=='cc' or form.tipo_operacion.data=='acf':
        #     movement=Movement(boleto_nro=boleto.id,
        #     fecha=boleto.fecha_concertacion,
        #     tipo_operacion=boleto.tipo_operacion,
        #     monto=-boleto.neto,
        #     tipo_cambio=boleto.tipo_cambio,
        #     alyc_id=boleto.alyc_id)
        try:
            # add boleto to the database
            # db.session.add(boleto)
            # db.session.add(movement)
            # db.session.commit()
            add_boleto_raw({'numero' : form.numero.data,
                            'fecha_concertacion' : form.fecha_concertacion.data,
                            'fecha_liquidacion':form.fecha_liquidacion.data,
                            'tipo_operacion':form.tipo_operacion.data,
                            'symbol':form.tiker.data,
                            'cantidad':form.cantidad.data,
                            'bruto':form.bruto.data,
                            'arancel':form.arancel.data,
                            'perc_arancel':form.perc_arancel.data,
                            'mercado_importe':form.mercado_importe.data,
                            'neto':form.neto.data,
                            'iva':form.iva.data,
                            'moneda':form.moneda.data,
                            'tipo_cambio':form.tipo_cambio.data,
                            'tipo_cambio_arancel':form.tipo_cambio_arancel.data,
                            'alyc_id':form.alyc_id.data.id,
                            'shares':[{'volume':share.volume.data,'price':share.price.data} for share in form.shares]})
        except Exception as e:
            # in case boleto name already exists
            flash(str(e))
        # if form.tipo_operacion.data=='vc' or form.tipo_operacion.data=='cc':
        #     try:
        #         add_stock(boleto.id,form.shares,form.tiker.data,form.tipo_operacion.data,form.fecha_liquidacion.data,0)
        #     except Exception as e:
        #         # in case boleto name already exists
        #         flash(str(e))
        return redirect(url_for('boletos.list_boletos'))
        # redirect to boletos page
        #return redirect(url_for('boletos.add_ticker', boleto_id=boleto.id))

    # load boleto template
    return render_template('boletos/boleto.html', action="Add",
                           add_boleto=True, form=form,
                           title="Add Boleto")


@boletos.route('/boletos/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_boleto(id):
    """
    Edit a boletos
    """


    add_boleto = False

    boleto = Boleto.query.get_or_404(id)
    form = BoletoForm(obj=boleto)
    if form.validate_on_submit():
        boleto.name = form.name.data
        boleto.contraparte = form.contraparte.data
        boleto.commitent = form.commitent.data
        db.session.commit()
        flash('You have successfully edited the boleto.')

        # redirect to the boletos page
        return redirect(url_for('boletos.list_boletos'))

    form.contraparte.data = boleto.contraparte
    form.commitent.data = boleto.commitent
    form.name.data = boleto.name
    return render_template('boletos/boleto.html', action="Edit",
                           add_boleto=add_boleto, form=form,
                           boleto=boleto, title="Edit boleto")


@boletos.route('/boletos/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_boleto(id):
    """
    Delete a boleto from the database
    """


    boleto = Boleto.query.get_or_404(id)
    db.session.delete(boleto)
    db.session.commit()
    flash('You have successfully deleted the boleto.')

    # redirect to the boletos page
    return redirect(url_for('boletos.list_boletos'))

    return render_template(title="Delete Boleto")

# @boletos.route('/boletos/accion/add/<boleto_id>', methods=['GET', 'POST'])
# @login_required
# def add_ticker(boleto_id):
#     """
#     Add a ticker to the database
#     """
#
#
#     add_ticker = True
#     boleto = Boleto.query.get_or_404(boleto_id)
#     form = TickerForm()
#     cantidad=boleto.cantidad
#     if form.validate_on_submit():
#         ticker = Share(tiker=form.tiker.data,
#                                 type=form.type.data,
#                                 quantity=form.quantity.data,
#                                 price = form.price.data,
#                                 date = form.date.data,
#                                 boleto_id = form.boleto_id.data,
#                                 dolar = 0)
#         if form.type.data =='vc':
#             portfolio=Portfolio.query.filter_by(ticker=form.tiker.data).first()
#             portfolio.quantity=portfolio.quantity-form.quantity.data
#         else:
#             try:
#                 portfolio=Portfolio.query.filter_by(ticker=form.tiker.data).first()
#                 portfolio.quantity=portfolio.quantity+form.quantity.data
#             except:
#                 portfolio=Portfolio(ticker=form.tiker.data,quantity=form.quantity.data,dolar=form.dolar.data)
#         try:
#             # add boleto to the database
#             db.session.add(ticker)
#             db.session.add(portfolio)
#             db.session.commit()
#             flash('You have successfully added a new boleto.')
#         except Exception as e:
#             # in case boleto name already exists
#             flash(str(e))
#         print(cantidad)
#         if cantidad != form.quantity.data:
#             cantidad=cantidad - form.quantity.data
#             form.price.data=0
#             form.quantity.data=cantidad
#             return render_template('boletos/ticker.html', action="Add",
#                                    add_boleto=add_ticker, form=form,
#                                    title="Add other Boleto")
#         else:
#             return render_template('boletos/boleto.html', action="Edit",
#                                add_boleto=add_boleto, form=form,
#                                boleto=boleto, title="Edit boleto")
#         # redirect to boletos page
#         return redirect(url_for('boletos.add_ticker'))
#
#     form.date.data = boleto.fecha_liquidacion
#     form.tiker.data = boleto.tiker
#     form.boleto_id.data = boleto.numero
#     form.type.data = boleto.tipo_operacion
#     # load boleto template
#     return render_template('boletos/ticker.html', action="Add",
#                            add_boleto=add_ticker, form=form,
#                            title="Add Boleto")




def add_orders(action_date,price,volume,type,symbol,tp=0,sl=0):
    result = db.engine.execute("select * from orders where sell_date is null and symbol='{}'".format(symbol)).fetchone()
    print(action_date,price,volume,type,symbol)
    if result:
        order = Order.query.get_or_404(result['id'])
    print(result)
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
    #db.session.commit()

@boletos.route('/order/bulk', methods=['POST'])
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

@boletos.route('/movimientos/bulk', methods=['POST'])
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

@boletos.route('/get_order/<symbol>', methods=['GET'])
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

@boletos.route('/get_orders', methods=['GET'])
def get_orders():
    orders=[]
    result = db.engine.execute("select * from orders where status ='open')").fetchall()
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

def add_boleto_raw(data):
    boleto = Boleto(numero = data['numero'],
                    fecha_concertacion = data['fecha_concertacion'],
                    fecha_liquidacion=data['fecha_liquidacion'],
                    tipo_operacion=data['tipo_operacion'],
                    tiker=data['tiker'],
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
                    alyc_id=data['alyc_id'])
    db.session.add(boleto)
    #db.session.commit()
    print('agregue el boleto')
    if  data['tipo_operacion']=='vc' :
        print('Agregue movimietno venta')
        movement=Movement(boleto_nro=boleto.id,
        fecha=boleto.fecha_concertacion,
        tipo_operacion=boleto.tipo_operacion,
        monto=boleto.neto,
        moneda=boleto.moneda,
        tipo_cambio=boleto.tipo_cambio,
        alyc_id=boleto.alyc_id)
    elif  data['tipo_operacion']=='acf':
        print('Agregue movimietno acf')
        movement=Movement(boleto_nro=boleto.id,
        fecha=boleto.fecha_liquidacion,
        tipo_operacion=boleto.tipo_operacion,
        monto=boleto.neto,
        moneda=boleto.moneda,
        tipo_cambio=boleto.tipo_cambio,
        alyc_id=boleto.alyc_id)
    elif  data['tipo_operacion']=='cc' or data['tipo_operacion']=='acc':
        print('Agregue movimietno compra o apertura colocadora contado')
        movement=Movement(boleto_nro=boleto.id,
        fecha=boleto.fecha_concertacion,
        tipo_operacion=boleto.tipo_operacion,
        monto=-boleto.neto,
        moneda=boleto.moneda,
        tipo_cambio=boleto.tipo_cambio,
        alyc_id=boleto.alyc_id)
    print('commit movimiento')
    db.session.add(movement)
    #db.session.commit()
    if data['tipo_operacion']=='vc' or data['tipo_operacion']=='cc':
        print('voy a shares')
        add_stock(boleto.id,data)


def add_stock(boleto_id,data):
    """
    Add a ticker to the database
    """
    print('vine a shares')
    print(data)
    precio_promedio=0
    for share in data['shares']:
        ticker = Share(tiker=symbol,
                                type=type,
                                quantity=share.volume.data,
                                price = share.price.data,
                                date = concertation_date,
                                boleto_id = boleto_id,
                                dolar = dolar)
        precio_promedio=share['price']*share['volume']+precio_promedio
    precio_promedio=precio_promedio/data['cantidad']
        # if type =='vc':
        #     portfolio=Portfolio.query.filter_by(ticker=symbol).first()
        #     portfolio.quantity=portfolio.quantity-share.volume.data
        # else:
        #     # try:
        #     #     portfolio=Portfolio.query.filter_by(ticker=symbol).first()
        #     #     portfolio.quantity=portfolio.quantity+share.volume.data
        #     # except:
        #     #     portfolio=Portfolio(ticker=symbol,quantity=share.volume.data,dolar=dolar)
        add_orders(data['fecha_concertacion'],precio_promedio,data['cantidad'],data['tipo_operacion'],data['symbol'],tp=0,sl=0):
        db.session.add(ticker)
        db.session.add(portfolio)
        #db.session.commit()
        flash('You have successfully added a new boleto.')

@boletos.route('/boletos/bulk', methods=['POST'])
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
