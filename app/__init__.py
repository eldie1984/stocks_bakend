import dash
import os
from flask import Flask
from flask.helpers import get_root_path
from flask_login import login_required
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import BaseConfig
from flask_bootstrap import Bootstrap




def create_app():
    template_dir = os.path.abspath('app/webapp/templates')
    server = Flask(__name__,template_folder=template_dir)
    server.config.from_object(BaseConfig)
    register_extensions(server)
    register_blueprints(server)

    return server

def register_extensions(server):
    from app.extensions import db
    from app.extensions import login_manager
    from app.extensions import migrate

    Bootstrap(server)
    db.init_app(server)
    login_manager.init_app(server)
    login_manager.login_message = "You must be logged in to access this page."
    login_manager.login_view = "auth.login"
    migrate.init_app(server, db)


def register_blueprints(server):

    from .webapp import models

    from .webapp.admin import admin as admin_blueprint
    server.register_blueprint(admin_blueprint, url_prefix='/admin')

    from .webapp.auth import auth as auth_blueprint
    server.register_blueprint(auth_blueprint)

    from .webapp.home import home as home_blueprint
    server.register_blueprint(home_blueprint)

    from .webapp.boletos import boletos as boletos_blueprint
    server.register_blueprint(boletos_blueprint)

    from .webapp.rest import rests as rest_blueprint
    server.register_blueprint(rest_blueprint)
