# Forms for admin blueprint
from flask_wtf import FlaskForm,Form
from wtforms import StringField, SubmitField,IntegerField,FloatField,DateField,SelectField,BooleanField,FieldList,FormField
from wtforms.validators import DataRequired,Optional
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Alyc

class TickerForm(Form):
    """
    Form template to add a tiker
    """
    volume=IntegerField('volume')
    price=FloatField('Precio')


class BoletosForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    numero = IntegerField('Numero', validators=[DataRequired()])
    fecha_concertacion = DateField('Fecha Concertacion')
    fecha_liquidacion=DateField('Fecha Liquidacion')
    cantidad=IntegerField('Cantidad', validators=[DataRequired()],render_kw={'readonly': True})
    tipo_operacion=SelectField('Tipo Operacion', choices=[('cc', 'Compra Contado'),('vc','Venta Contado'),('acc', 'Apertura Colocadora Contado'), ('acf', 'Apertura Colocadora Futuro'),('ocl','Opción Compra Lanzador (Call Venta)'),('atc','Apertura Tomadora Contado (Tipo Caución)'),('atf','Apertura Tomadora Futuro (Tipo Caución)'),('lc','Licitación Compra')])
    tiker=StringField('Ticker', validators=[Optional()])
    arancel=FloatField('Arancel', validators=[Optional()])
    perc_arancel=FloatField('Porcentaje', validators=[Optional()],render_kw={'readonly': True})
    mercado_importe=FloatField('Mercado Importe', validators=[DataRequired()])
    iva=BooleanField('Iva')
    shares=FieldList(FormField(TickerForm),validators=[Optional()])
    bruto=FloatField('Bruto', validators=[DataRequired()],render_kw={'readonly': True})
    neto=FloatField('Neto', validators=[DataRequired()])
    moneda=SelectField(u'Moneda', choices=[('p', 'Pesos'), ('d', 'Dolar')],default='p')
    tipo_cambio=FloatField('Tipo Cambio', default=1)
    tipo_cambio_arancel=FloatField('Tipo Cambio Arancel', default=1)
    interes=FloatField('Interes',validators=[Optional()])
    alyc_id=QuerySelectField(query_factory=lambda: Alyc.query.all(),
                                  get_label="name")
    submit = SubmitField('Submit')


class MoventForm(FlaskForm):
    numero = IntegerField('Numero', validators=[Optional()])
    fecha_concertacion = DateField('Fecha Concertacion')
    tipo_operacion=SelectField('Tipo Operacion', choices=[
                                        ('cc', 'Compra Contado')
                                        ,('vc','Venta Contado')
                                        ,('acc', 'Apertura Colocadora Contado'),
                                         ('acf', 'Apertura Colocadora Futuro')
                                         ,('ocl','Opción Compra Lanzador (Call Venta)')
                                         ,('atc','Apertura Tomadora Contado (Tipo Caución)')
                                         ,('atf','Apertura Tomadora Futuro (Tipo Caución)')
                                         ,('lc','Licitación Compra')
                                         ,('ing','Ingreso')
                                         ,('div','Dividendo')
                                         ,('ven','Vencimiento')
                                         ,('ren','Renta')
                                         ,('ext','Extraccion')
                                         ,('com','Comision')])
    boleto=FormField()
    monto=FloatField('Arancel', validators=[Optional()])
    moneda=SelectField(u'Moneda', choices=[('p', 'Pesos'), ('d', 'Dolar')],default='p')
    descripcion=StringField('Descripcion', validators=[Optional()])
    alyc_id=QuerySelectField(query_factory=lambda: Alyc.query.all(),
                                  get_label="name")
    submit = SubmitField('Submit')

class SymbolForm(FlaskForm):
    symbol=StringField('Symbol', validators=[DataRequired()],render_kw={'readonly': True})
    follow=BooleanField('Follow')
    description=StringField('Description', validators=[Optional()])
    yf=StringField('Yahho', validators=[Optional()])
    ppi=StringField('PPI', validators=[Optional()])
    rava=StringField('Rava', validators=[Optional()])

class DividendosForm(FlaskForm):
    monto=FloatField('Arancel', validators=[Optional()])
    moneda=SelectField(u'Moneda', choices=[('p', 'Pesos'), ('d', 'Dolar')],default='p')
    cantidad=IntegerField('Cantidad', validators=[DataRequired()],render_kw={'readonly': True})
