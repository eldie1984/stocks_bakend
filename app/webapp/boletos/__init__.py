from flask import Blueprint

boletos = Blueprint('boletos', __name__)

from . import views
