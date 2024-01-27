"""User model for SQLAlchemy"""

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)
    bcrypt.init_app(app)
    

class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)

    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)

    @classmethod
    def get_users(cls):
        return cls.query.all()
    
    @classmethod
    def find_user(cls, username):
        return cls.query.get_or_404(username)
    
    @classmethod
    def register(cls, username, pwd, email, first_name, last_name):
        hashed_pwd = bcrypt.generate_password_hash(pwd).decode("utf-8")
        return cls(username=username, password=hashed_pwd, email=email, first_name=first_name, last_name=last_name)

    @classmethod
    def authenticate(cls, username, pwd):
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, pwd):
            return user
        else:
            return False

