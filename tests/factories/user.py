from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.models.user import UserModel


class UserFactory(SQLAlchemyFactory[UserModel]):
    __model__ = UserModel

    cart = Ignore()
    orders = Ignore()

    @classmethod
    def hashed_password(cls):
        return cls.__faker__.sha256()
