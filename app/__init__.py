from flask import Flask
from flask_login import LoginManager
from flask_babel import Babel
from .config import Config
from .db import DB


login = LoginManager()
login.login_view = 'users.login'
babel = Babel()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)
    login.init_app(app)
    babel.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    from .cart import bp as cart_bp
    app.register_blueprint(cart_bp)

    from .inventory import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from .sellerhistory import bp as sellerhistory_bp
    app.register_blueprint(sellerhistory_bp)

    from .public import bp as public_bp
    app.register_blueprint(public_bp)

    return app