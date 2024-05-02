from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.products import ProductDoesNotExistError
from core.receipts import (
    Receipt,
    ReceiptClosedError,
    ReceiptDoesNotExistError,
    ReceiptProduct,
)
from infra.fastapi.dependables import ReceiptServiceDependable
from infra.fastapi.http_exceptions import DoesNotExistResponse

receipt_api = APIRouter(tags=["Receipts"])


class CreateReceiptRequest(BaseModel):
    pass


class ReceiptProductItem(BaseModel):
    id: UUID
    quantity: int
    price: float
    total: float


class ReceiptItem(BaseModel):
    id: UUID
    status: str
    products: list[ReceiptProductItem]
    total: float


def convert_product_for_response(product: ReceiptProduct) -> ReceiptProductItem:
    return ReceiptProductItem(
        id=product.inner.id,
        quantity=product.quantity,
        price=product.inner.price,
        total=product.get_total(),
    )


def convert_receipt_for_response(receipt: Receipt) -> ReceiptItem:
    products_for_response = [
        convert_product_for_response(product) for product in receipt.products
    ]

    return ReceiptItem(
        id=receipt.id,
        status=receipt.status,
        products=products_for_response,
        total=receipt.get_total(),
    )


class ReceiptItemEnvelope(BaseModel):
    receipt: ReceiptItem


class AddProductToReceiptRequest(BaseModel):
    id: UUID
    quantity: int


class CloseReceiptRequest(BaseModel):
    status: str


@receipt_api.post(
    "/receipts",
    status_code=status.HTTP_201_CREATED,
    response_model=ReceiptItemEnvelope,
)
def create_receipt(receipt_service: ReceiptServiceDependable) -> dict[str, ReceiptItem]:
    created_receipt = receipt_service.create_receipt()
    return {"receipt": convert_receipt_for_response(created_receipt)}


@receipt_api.post(
    "/receipts/{receipt_id}/products",
    status_code=status.HTTP_201_CREATED,
    response_model=ReceiptItemEnvelope,
)
def add_product_to_receipt(
    receipt_id: UUID,
    request: AddProductToReceiptRequest,
    receipt_service: ReceiptServiceDependable,
) -> dict[str, ReceiptItem]:
    try:
        updated_receipt = receipt_service.add_product(
            receipt_id, request.id, request.quantity
        )
        return {"receipt": convert_receipt_for_response(updated_receipt)}
    except (
        ReceiptDoesNotExistError,
        ProductDoesNotExistError,
        ReceiptClosedError,
    ) as e:
        if isinstance(e, ReceiptDoesNotExistError):
            raise DoesNotExistResponse(item_type="Receipt", item_id=receipt_id) from e
        if isinstance(e, ProductDoesNotExistError):
            raise DoesNotExistResponse(item_type="Product", item_id=request.id) from e
        if isinstance(e, ReceiptClosedError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {"message": f"Receipt with id {receipt_id} is closed."}
                },
            ) from e


@receipt_api.get(
    "/receipts/{receipt_id}",
    response_model=ReceiptItemEnvelope,
)
def read_receipt(
    receipt_id: UUID, receipt_service: ReceiptServiceDependable
) -> dict[str, ReceiptItem]:
    try:
        receipt = receipt_service.read_receipt(receipt_id)
        return {"receipt": convert_receipt_for_response(receipt)}
    except ReceiptDoesNotExistError as e:
        # raise ReceiptDoesNotExistResponse(receipt_id) from e
        raise DoesNotExistResponse(item_type="Receipt", item_id=receipt_id) from e


@receipt_api.patch(
    "/receipts/{receipt_id}",
    status_code=status.HTTP_200_OK,
)
def close_receipt(
    receipt_id: UUID,
    request: CloseReceiptRequest,
    receipt_service: ReceiptServiceDependable,
) -> dict[str, Any]:
    try:
        receipt_service.update_receipt_status(receipt_id, request.status)
        return {}
    except ReceiptDoesNotExistError as e:
        # raise ReceiptDoesNotExistResponse(receipt_id)
        raise DoesNotExistResponse(item_type="Receipt", item_id=receipt_id) from e


@receipt_api.delete(
    "/receipts/{receipt_id}",
    status_code=status.HTTP_200_OK,
)
def delete_receipt(
    receipt_id: UUID, receipt_service: ReceiptServiceDependable
) -> dict[str, Any]:
    try:
        receipt_service.delete_receipt(receipt_id)
        return {}
    except (ReceiptDoesNotExistError, ReceiptClosedError) as e:
        if isinstance(e, ReceiptDoesNotExistError):
            # raise ReceiptDoesNotExistResponse
            raise DoesNotExistResponse(item_type="Receipt", item_id=receipt_id) from e
        if isinstance(e, ReceiptClosedError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {"message": f"Receipt with id {receipt_id} is closed."}
                },
            ) from e
