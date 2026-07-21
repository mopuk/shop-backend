from .auth import router as auth_router
from .products import router as products_router
from .cart import router as cart_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(auth_router)
router.include_router(products_router)
router.include_router(cart_router)

@router.get("/")
def root():
    return {"message": "Backend"}
