# Views for boletos blueprint
from flask import abort, flash, redirect, render_template, url_for,request
from flask_login import current_user, login_required
from sqlalchemy import func
import json

from . import boletos
from .forms import BoletosForm,TickerForm
from ...extensions import db
from ..models import Boleto,Movement
from ..functions import *

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
        try:
            add_boleto_raw({'numero' : form.numero.data,
                            'fecha_concertacion' : form.fecha_concertacion.data,
                            'fecha_liquidacion':form.fecha_liquidacion.data,
                            'tipo_operacion':form.tipo_operacion.data,
                            'symbol':form.tiker.data.upper(),
                            'cantidad':form.cantidad.data,
                            'bruto':form.bruto.data,
                            'arancel':form.arancel.data,
                            'perc_arancel':form.perc_arancel.data,
                            'mercado_importe':form.mercado_importe.data,
                            'neto':form.neto.data,
                            'iva':form.iva.data,
                            'interes':form.interes.data,
                            'moneda':form.moneda.data,
                            'tipo_cambio':form.tipo_cambio.data,
                            'tipo_cambio_arancel':form.tipo_cambio_arancel.data,
                            'alyc_id':form.alyc_id.data.id,
                            'shares':[{'volume':share.volume.data,'price':share.price.data} for share in form.shares]})
            flash('You have successfully added a new boleto.')
        except Exception as e:
            # in case boleto name already exists
            flash(str(e))
        return redirect(url_for('boletos.list_boletos'))
        # redirect to boletos page

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
