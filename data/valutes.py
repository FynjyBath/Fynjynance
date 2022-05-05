import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import check_password_hash, generate_password_hash
from .db_session import SqlAlchemyBase


class Valute(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'valutes'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    img_direct = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    volatil = sqlalchemy.Column(sqlalchemy.Integer, default=1)
    sovalute_name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
