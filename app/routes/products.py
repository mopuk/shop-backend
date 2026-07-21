from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.models.product import ProductModel, ProductVariantModel, CategoryModel, BrandModel, ProductSizeModel, ProductMaterialModel, ProductColorModel
from app.schemas.product import BrandListResponse, ProductVariantListResponse, CategoryListResponse, FiltersListResponse, ProductSchema
from app.database import get_db

router = APIRouter(
    prefix="/api/v1",
    tags=["products"]
    )


@router.get("/products", response_model=ProductVariantListResponse)
async def get_products(
        db: Annotated[AsyncSession, Depends(get_db)],
        featured: bool = False,
        category: str | None = None,
        brand: str | None = None,
        size: str | None = None,
        material: str | None = None,
        color: str | None = None,
    ):
    
    smtm = select(ProductVariantModel).options(
        selectinload(ProductVariantModel.images),
        joinedload(ProductVariantModel.material),
        joinedload(ProductVariantModel.size),
        joinedload(ProductVariantModel.color),
        joinedload(ProductVariantModel.product).options(
                selectinload(ProductModel.brand),
                selectinload(ProductModel.category)
            )
        )  
    
    if featured:
        smtm = smtm.where(
            ProductVariantModel.product.has(
                ProductModel.is_featured == True
                )
            )
        
    if category:
        smtm = smtm.where(
            ProductVariantModel.product.has(
                ProductModel.category.has(CategoryModel.slug == category)
                )
            )
    if brand:
        smtm = smtm.where(
            ProductVariantModel.product.has(
                ProductModel.brand.has(BrandModel.slug == brand)
                )
            )
    if size:
        smtm = smtm.where(
            ProductVariantModel.size.has(ProductSizeModel.name == size)
            )
    if material:
        smtm = smtm.where(
            ProductVariantModel.material.has(ProductMaterialModel.slug == material)
            )
    if color:
        smtm = smtm.where(
            ProductVariantModel.color.has(ProductColorModel.slug == color)
            )
    
    variants = await db.scalars(smtm)
    return {
    "variants": variants.unique().all()
}
    
@router.get("/products/filters", response_model=FiltersListResponse)
async def get_filters(db: Annotated[AsyncSession, Depends(get_db)]):
    sizes = await db.scalars(
        select(ProductSizeModel)
        .join(ProductVariantModel)
        .distinct()
        .order_by(ProductSizeModel.sort_order)
        )
    colors = await db.scalars(
        select(ProductColorModel)
        .join(ProductVariantModel)
        .distinct()
        )
    materials = await db.scalars(
        select(ProductMaterialModel)
        .join(ProductVariantModel)
        .distinct()
        )
    
    return {
        "sizes": sizes.all(),
        "colors": colors.all(),
        "materials": materials.all(),
    }



@router.get("/products/{product_slug}", response_model=ProductSchema)
async def get_product(product_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    
    try:
        smtm = select(ProductModel).options(
                selectinload(ProductModel.variants).options(
                    selectinload(ProductVariantModel.images),
                    joinedload(ProductVariantModel.color),
                    joinedload(ProductVariantModel.material),
                    joinedload(ProductVariantModel.size),
                ),
                selectinload(ProductModel.category),
                selectinload(ProductModel.brand),
            ).where(ProductModel.slug == product_slug)
        result = await db.execute(smtm)
        product = result.scalar_one_or_none()
    except SQLAlchemyError:
        raise HTTPException(500, "Error in the database")
    if not product:
        raise HTTPException(404, f"Product with slug: {product_slug} is not found")
        
    return product

@router.get("/categories", response_model=CategoryListResponse)
async def get_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    
    categories = await db.execute(select(CategoryModel))

    return {
        "categories": categories.scalars().all()
    }
    

@router.get("/brands", response_model=BrandListResponse)
async def get_brands(db: Annotated[AsyncSession, Depends(get_db)]):
    
    brands = await db.scalars(select(BrandModel))

    return {
        "brands": brands.all()
    }
    
# Delete later, obsolete beacuse of /products
""" 
@router.get("/brands/{brand_slug}/products")
async def get_products_by_brand(brand_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):

    smtm = select(ProductVariantModel).join(ProductModel).join(BrandModel).options(
                selectinload(ProductVariantModel.images),
                selectinload(ProductVariantModel.size),
                selectinload(ProductVariantModel.color),
                selectinload(ProductVariantModel.material),
                joinedload(ProductVariantModel.product).options(
                    selectinload(ProductModel.category),
                    selectinload(ProductModel.brand)
                )
            ).where(BrandModel.slug == brand_slug)
    
    variants = await db.execute(smtm)
    return {
        "variants": variants.scalars().all()
    }
 """
 # Delete later, obsolete beacuse of /products
"""     
@router.get("/categories/{category_slug}")
async def get_products_by_category(category_slug: str, db: Annotated[AsyncSession, Depends(get_db)]):
    
    smtm = (select(ProductVariantModel)
        .join(ProductVariantModel.product)
        .join(ProductModel.category)
        .options(
            selectinload(ProductVariantModel.images),
            selectinload(ProductVariantModel.size),
            selectinload(ProductVariantModel.color),
            selectinload(ProductVariantModel.material),
            joinedload(ProductVariantModel.product).options(
                selectinload(ProductModel.category),
                selectinload(ProductModel.brand)
            )
        ).where(ProductVariantModel.product.has(
                    ProductModel.category == category_slug)
            )
    )
    variants = await db.scalars(smtm)
    return {
    "variants": variants
}
 """
 # Delete later, obsolete beacuse of /products
""" 
@router.get("/products/featured")
async def get_featured_products(db: Annotated[AsyncSession, Depends(get_db)]):

    smtm = select(ProductModel).options(
            selectinload(ProductModel.variants).options(
                selectinload(ProductVariantModel.images),
                joinedload(ProductVariantModel.color),
                joinedload(ProductVariantModel.material),
                joinedload(ProductVariantModel.size),
                ),
            selectinload(ProductModel.brand),
            selectinload(ProductModel.category),
        ).where(ProductModel.is_featured == True)

    products = await db.scalars(smtm)
    return {
        "products": products
    } """