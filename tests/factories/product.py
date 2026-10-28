from decimal import Decimal

from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.models.product import *


class ProductFactory(SQLAlchemyFactory[ProductModel]):
    __model__ = ProductModel

    variants = Ignore()
    category = Ignore()
    brand = Ignore()

    @classmethod
    def base_price(cls):
        random_float = cls.__random__.uniform(10.0, 500.0)
        return Decimal(str(random_float)).quantize(Decimal("0.01"))

    @classmethod
    def name(cls):
        return cls.__faker__.ecommerce_name()

    @classmethod
    def slug(cls):
        return cls.__faker__.slug()

    @classmethod
    def thumbnail(cls) -> str:
        return cls.__faker__.image_url()


class ProductVariantFactory(SQLAlchemyFactory[ProductVariantModel]):
    __model__ = ProductVariantModel

    size = Ignore()
    color = Ignore()
    material = Ignore()
    product = Ignore()
    images = Ignore()

    @classmethod
    def stock(cls):
        return cls.__random__.randint(0, 500)

    @classmethod
    def thumbnail(cls) -> str:
        return cls.__faker__.image_url()

    @classmethod
    def variant_price(cls):
        random_float = cls.__random__.uniform(10.0, 500.0)
        return Decimal(str(random_float)).quantize(Decimal("0.01"))


class ProductImageFactory(SQLAlchemyFactory[ProductImageModel]):
    __model__ = ProductImageModel

    variant = Ignore()

    @classmethod
    def url(cls):
        return cls.__faker__.url()

    @classmethod
    def sort_order(cls):
        return cls.__random__.randint(1, 10)


class ProductSizeFactory(SQLAlchemyFactory[ProductSizeModel]):
    __model__ = ProductSizeModel

    variants = Ignore()

    @classmethod
    def sort_order(cls):
        return cls.__random__.randint(1, 10)


class ProductColorFactory(SQLAlchemyFactory[ProductColorModel]):
    __model__ = ProductColorModel

    variants = Ignore()

    @classmethod
    def hex_code(cls):
        return cls.__faker__.hex_color()

    @classmethod
    def name(cls):
        return cls.__faker__.color_name()

    @classmethod
    def slug(cls):
        return cls.__faker__.slug()


class ProductMaterialFactory(SQLAlchemyFactory[ProductMaterialModel]):
    __model__ = ProductMaterialModel

    variants = Ignore()

    @classmethod
    def slug(cls):
        return cls.__faker__.slug()


class CategoryFactory(SQLAlchemyFactory[CategoryModel]):
    __model__ = CategoryModel

    parent_id = Ignore()
    parent = Ignore()
    children = Ignore()
    products = Ignore()

    @classmethod
    def slug(cls):
        return cls.__faker__.slug()


class BrandFactory(SQLAlchemyFactory[BrandModel]):
    __model__ = BrandModel

    products = Ignore()

    @classmethod
    def slug(cls):
        return cls.__faker__.slug()
