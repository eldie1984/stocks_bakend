from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db, login_manager


class Employee(UserMixin, db.Model):
    """
    Create an Employee table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    alycs = db.relationship('Alyc', backref='employees',
                                lazy='dynamic')

    @property
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Employee: {}>'.format(self.username)


# Set up user_loader
@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))


class Share(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'shares'

    id = db.Column(db.Integer, primary_key=True)
    tiker = db.Column(db.String(60))
    type = db.Column(db.String(3))
    quantity = db.Column(db.Integer)
    price=db.Column(db.Float)
    date=db.Column(db.DateTime)
    boleto_id = db.Column(db.Integer)
    dolar=db.Column(db.Integer)

class Portfolio(db.Model):
    """
    Create a Department table
    """

    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(60),unique=True)
    quantity = db.Column(db.Integer)
    dolar=db.Column(db.Integer)

class Order(db.Model):
    """
    Create a Orders table
    """

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    buy_date = db.Column(db.DateTime)
    type = db.Column(db.String(10))
    volume=db.Column(db.Integer)
    symbol=db.Column(db.String(7))
    tp=db.Column(db.Float)
    sl=db.Column(db.Float)
    price=db.Column(db.Float)
    price_usd=db.Column(db.Float)
    profit=db.Column(db.Float)
    profit_amount=db.Column(db.Float)
    profit_amount_usd=db.Column(db.Float)
    sell_price=db.Column(db.Float)
    sell_date=db.Column(db.DateTime)
    sell_price_usd=db.Column(db.Float)
    status=db.Column(db.String(10))

class Alyc(db.Model):
    """
    Create a Alyc table
    """

    __tablename__ = 'alycs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    contraparte=db.Column(db.Integer)
    commitent=db.Column(db.Integer)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))


    def __repr__(self):
        return '<Alyc: {}>'.format(self.name)


class Boleto(db.Model):
    """
    Create a Role table
    """

    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer)
    fecha_concertacion=db.Column(db.DateTime)
    fecha_liquidacion=db.Column(db.DateTime)
    tipo_operacion=db.Column(db.String(3))
    tiker=db.Column(db.String(10))
    cantidad = db.Column(db.Integer)
    precio_promedio=db.Column(db.Float)
    bruto=db.Column(db.Float)
    arancel=db.Column(db.Float)
    perc_arancel=db.Column(db.Float)
    mercado_importe=db.Column(db.Float)
    neto=db.Column(db.Float)
    moneda=db.Column(db.String(2))
    tipo_cambio_arancel=db.Column(db.Float)
    tipo_cambio=db.Column(db.Float)
    iva=db.Column(db.Boolean)
    interes=db.Column(db.Float)
    alyc_id=db.Column(db.Integer, db.ForeignKey('alycs.id'))
    # shares = db.relationship('Share', backref='tickets',
    #                             lazy='dynamic')
class Movement(db.Model):
    """
    Create a Role table
    """

    __tablename__ = 'movements'

    id = db.Column(db.Integer, primary_key=True)
    boleto_nro=db.Column(db.Integer)
    fecha=db.Column(db.DateTime)
    tipo_operacion=db.Column(db.String(3))
    monto=db.Column(db.Float)
    moneda=db.Column(db.String(2))
    tipo_cambio=db.Column(db.Float)
    descripcion=db.Column(db.String(200))
    alyc_id=db.Column(db.Integer, db.ForeignKey('alycs.id'))


class Follow(db.Model):
    """
    Create a Role table
    """

    __tablename__ = 'follow'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10))
    ppi=db.Column(db.String(50))
    rava=db.Column(db.String(50))
    iol=db.Column(db.String(50))
    follow=db.Column(db.Boolean)
    descricion=db.Column(db.String(300))
    @property
    def serialize(self):
       """Return object data in easily serializable format"""
       return {
           'symbol'         : self.symbol,
           'ppi': self.ppi,
           'rava': self.rava,
           'iol': self.iol
       }
