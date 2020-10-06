from flask import Blueprint

rests = Blueprint('rest', __name__)

from . import views
