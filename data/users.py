import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    phone = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    NEAR = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    Bitcoin = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    Fynjycoin = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    Saratovcoin = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    Evgrocoin = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    euro = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    dollar = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    rubl = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    photo_way = sqlalchemy.Column(sqlalchemy.String, default='/static/img/no_photo.png')
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f'<Colonist> {self.id} {self.surname} {self.name}'
