from fastapi import APIRouter, HTTPException, status
from app.schemas.product.productSchemas import ProductRequest, ProductResponse
from app.services.product.productService import create_product_db, get_product_db, update_product_db, delete_product_db

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_route(product: ProductRequest):
    product_id = create_product_db(product.category, product.name, product.description, product.price, product.stock, product.image_url)
    if not product_id:
        raise HTTPException(status_code=500, detail="Error creating product")
    return {"id": product_id, **product.dict()}

@router.get("/{product_id}", response_model=ProductResponse)
def get_product_route(product_id: int):
    product = get_product_db(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_product_route(product_id: int, product: ProductRequest):
    if not update_product_db(product_id, product.category, product.name, product.description, product.price, product.stock, product.image_url):
        raise HTTPException(status_code=404, detail="Product not found")

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product_route(product_id: int):
    if not delete_product_db(product_id):
        raise HTTPException(status_code=404, detail="Product not found")