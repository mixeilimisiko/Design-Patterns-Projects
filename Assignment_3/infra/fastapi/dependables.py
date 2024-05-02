from typing import Annotated, Any, Union

from fastapi import Depends
from fastapi.requests import Request

from core.products import ProductService
from core.receipts import ReceiptService
from core.units import UnitService


def get_unit_service(request: Request) -> Union[UnitService, Any]:
    return request.app.state.unit_service


UnitServiceDependable = Annotated[UnitService, Depends(get_unit_service)]


def get_product_service(request: Request) -> Union[ProductService, Any]:
    return request.app.state.product_service


ProductServiceDependable = Annotated[ProductService, Depends(get_product_service)]


def get_receipt_service(request: Request) -> Union[ReceiptService, Any]:
    return request.app.state.receipt_service


ReceiptServiceDependable = Annotated[ReceiptService, Depends(get_receipt_service)]
