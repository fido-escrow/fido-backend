#src/models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


# initialize our db and bcrypt
db = SQLAlchemy()
bcrypt = Bcrypt()