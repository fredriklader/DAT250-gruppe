from flask import Flask, g
from config import Config
from flask_bootstrap import Bootstrap
import sqlite3
import os


#Nytt
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length

from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# create and configure app
app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
app.config['RECAPTCHA_PUBLIC_KEY'] = '6LdeHyIiAAAAAGDK0iEtE7ElIV3PBZY34D-y9CAS' #public key
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LdeHyIiAAAAAMChmfJyz-lRph0BIm0nEpoFctZq' #secret key
app.config['TESTING'] = False

# get an instance of the db
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db

# initialize db for the first time
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# perform generic query, not very secure yet
def query_db(query, one=False):
    db = get_db()
    cursor = db.execute(query)
    rv = cursor.fetchall()
    cursor.close()
    db.commit()
    return (rv[0] if rv else None) if one else rv

# TODO: Add more specific queries to simplify code

# automatically called when application is closed, and closes db connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# initialize db if it does not exist
if not os.path.exists(app.config['DATABASE']):
    init_db()

if not os.path.exists(app.config['UPLOAD_PATH']):
    os.mkdir(app.config['UPLOAD_PATH'])

from app import routes