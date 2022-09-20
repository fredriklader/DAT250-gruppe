import os
import string
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin

# contains application-wide configuration, and is loaded in __init__.py

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret' # TODO: Use this with wtforms
    DATABASE = 'database.db'
    UPLOAD_PATH = 'app/static/uploads'
    ALLOWED_EXTENSIONS = {} # Might use this at some point, probably don't want people to upload any file type

# class User(UserMixin,  db.Model):
#     """User account model."""
#     __tablename__ = 'flasklogin-users'
#     user_id =  db.Column(
#         db.Integer,
#         primary_key=True
#     )
#     username = db.Column(
#         db.String(100),
#         nullable=False,
#         unique=False
#     )
    
   
  



