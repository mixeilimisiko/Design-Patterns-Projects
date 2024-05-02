from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from core.products import Product, ProductDoesNotExistError, ProductExistsError
from core.units import UnitDoesNotExistError
from infra.fastapi.dependables import ProductServiceDependable
from infra.fastapi.http_exceptions import (
    CreateProductExceptionResponse,
    DoesNotExistResponse,
)

product_api = APIRouter(tags=["Products"])


class CreateProductRequest(BaseModel):
    unit_id: UUID
    name: str
    barcode: str
    price: float


class ProductItem(BaseModel):
    id: UUID
    unit_id: UUID
    name: str
    barcode: str
    price: float


class ProductItemEnvelope(BaseModel):
    product: ProductItem


class UpdateProductRequest(BaseModel):
    price: float


class FetchProductsResponse(BaseModel):
    products: list[ProductItem]


def convert_product(product: Product) -> ProductItem:
    return ProductItem(
        id=product.id,
        unit_id=product.unit_id,
        name=product.name,
        barcode=product.barcode,
        price=product.price,
    )


@product_api.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductItemEnvelope,
)
def create_product(
    request: CreateProductRequest, product_service: ProductServiceDependable
) -> dict[str, ProductItem]:
    try:
        created_product = product_service.create_product(
            unit_id=request.unit_id,
            name=request.name,
            barcode=request.barcode,
            price=request.price,
        )

        return {"product": convert_product(created_product)}
    except (UnitDoesNotExistError, ProductExistsError) as e:
        if isinstance(e, UnitDoesNotExistError):
            # raise ReadUnitExceptionResponse(request.unit_id) from e
            raise DoesNotExistResponse(item_type="Unit", item_id=request.unit_id) from e
        elif isinstance(e, ProductExistsError):
            raise CreateProductExceptionResponse(request.barcode) from e


@product_api.get(
    "/products/{product_id}",
    response_model=ProductItemEnvelope,
)
def fetch_product(
    product_id: UUID, product_service: ProductServiceDependable
) -> dict[str, ProductItem]:
    try:
        product = product_service.fetch(product_id)
        return {"product": convert_product(product)}
    except ProductDoesNotExistError as e:
        raise DoesNotExistResponse(item_type="Product", item_id=product_id) from e


@product_api.get("/products", response_model=FetchProductsResponse)
def fetch_all(
    product_service: ProductServiceDependable,
) -> dict[str, list[ProductItem]]:
    products = [
        convert_product(product) for product in product_service.fetch_all_products()
    ]
    return {"products": products}
    # return FetchProductsResponse(products=products)


@product_api.patch(
    "/products/{product_id}",
    # response_model=ProductItem,
)
def update_product(
    product_id: UUID,
    request: UpdateProductRequest,
    product_service: ProductServiceDependable,
) -> dict[str, str]:
    try:
        product_service.update_product(product_id, request.price)
        return {"message": "Product updated successfully"}
    except ProductDoesNotExistError as e:
        raise DoesNotExistResponse(item_type="Product", item_id=product_id) from e
