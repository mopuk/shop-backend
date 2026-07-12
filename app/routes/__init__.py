from .products import router as products_router
from fastapi import APIRouter

router = APIRouter()
router.include_router(products_router)

@router.get("/")
def root():
    return {"message": "Backend"}
