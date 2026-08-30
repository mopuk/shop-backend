from enum import Enum


class TargetGroup(Enum):
    men = "men"
    women = "women"
    unisex = "unisex"

class Role(Enum):
    customer = "customer"
    admin = "admin"

class OrderStatus(Enum):
    pending = "pending"
    paid = "paid"
    delivered = "delivered"
