from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_owned_product, get_owned_segment
from app.models import Product, Segment
from app.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(tags=["products"])


@router.get("/segments/{segment_id}/products", response_model=list[ProductRead])
def list_products(
    segment: Segment = Depends(get_owned_segment),
    db: Session = Depends(get_db),
) -> list[Product]:
    return db.query(Product).filter(Product.segment_id == segment.id).all()


@router.post(
    "/segments/{segment_id}/products",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    body: ProductCreate,
    segment: Segment = Depends(get_owned_segment),
    db: Session = Depends(get_db),
) -> Product:
    product = Product(segment_id=segment.id, **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.patch("/products/{product_id}", response_model=ProductRead)
def update_product(
    body: ProductUpdate,
    product: Product = Depends(get_owned_product),
    db: Session = Depends(get_db),
) -> Product:
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product: Product = Depends(get_owned_product),
    db: Session = Depends(get_db),
) -> None:
    db.delete(product)
    db.commit()
