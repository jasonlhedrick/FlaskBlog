from flask import Flask
from flask_mail import Mail
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.errors.handlers import errors

app = Flask(__name__)
app.config.from_object(Config)
app.config.secret_key = Config.SECRET_KEY
app.register_blueprint(errors)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from app import routes, models