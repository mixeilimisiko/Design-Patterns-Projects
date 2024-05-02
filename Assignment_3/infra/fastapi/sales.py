from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from infra.fastapi.dependables import ReceiptServiceDependable

sales_api = APIRouter(tags=["Sales"])


class ReportResponse(BaseModel):
    n_receipts: int
    revenue: float


class ReportResponseEnvelope(BaseModel):
    sales: ReportResponse


@sales_api.get("/sales", response_model=ReportResponseEnvelope, status_code=200)
def get_sales_report(
    receipt_service: ReceiptServiceDependable,
) -> dict[str, dict[str, Any]]:
    receipt_info = receipt_service.get_sales_report()
    n_receipts = receipt_info.total_sale_num
    revenue = receipt_info.total_revenue

    return {"sales": {"n_receipts": n_receipts, "revenue": revenue}}
