from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from core.products import Product, ProductDoesNotExistError, ProductRepository


class Sellable(Protocol):
    def get_total(self) -> float:
        pass


@dataclass
class ReceiptProduct:
    inner: Product
    quantity: int

    def get_total(self) -> float:
        return self.quantity * self.inner.price


@dataclass
class Receipt:
    status: str = "open"
    id: UUID = field(default_factory=uuid4)
    products: list[ReceiptProduct] = field(default_factory=list)

    def get_total(self) -> float:
        return sum(product.get_total() for product in self.products)

    def add_product(self, product: ReceiptProduct) -> None:
        self.products.append(product)


@dataclass
class ReportInfo:
    total_sale_num: int
    total_revenue: float


class ReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> None:
        pass

    def add_product(self, receipt_id: UUID, product: ReceiptProduct) -> None:
        pass

    def read(self, receipt_id: UUID) -> Receipt:
        pass

    def update_status(self, receipt_id: UUID, receipt_status: str) -> None:
        pass

    def delete(self, receipt_id: UUID) -> None:
        pass

    def read_all(self) -> list[Receipt]:
        pass


class ReceiptExistsError(Exception):
    pass


class ReceiptDoesNotExistError(Exception):
    pass


class ReceiptClosedError(Exception):
    pass


@dataclass
class ReceiptService:
    products: ProductRepository
    receipts: ReceiptRepository

    def create_receipt(self) -> Receipt:
        receipt = Receipt()
        self.receipts.create(receipt)
        return receipt

    def add_product(self, receipt_id: UUID, product_id: UUID, quantity: int) -> Receipt:
        # Check if the receipt exists
        receipt = Receipt()
        try:
            receipt = self.receipts.read(receipt_id)
        except ReceiptDoesNotExistError as e:
            raise e

        # Check if the product exists
        try:
            product = self.products.read(product_id)
            receipt_product = ReceiptProduct(inner=product, quantity=quantity)
            self.receipts.add_product(receipt_id, receipt_product)
            receipt.add_product(receipt_product)
        except ProductDoesNotExistError as e:
            raise e

        # Create a ReceiptProduct and add it to the receipt
        return receipt

    def read_receipt(self, receipt_id: UUID) -> Receipt:
        receipt = Receipt()
        try:
            receipt = self.receipts.read(receipt_id)
        except ReceiptDoesNotExistError as e:
            raise e
        return receipt

    def update_receipt_status(self, receipt_id: UUID, receipt_status: str) -> None:
        try:
            self.receipts.update_status(receipt_id, receipt_status)
        except ReceiptDoesNotExistError as e:
            raise e

    def delete_receipt(self, receipt_id: UUID) -> None:
        try:
            self.receipts.delete(receipt_id)
        except (ReceiptDoesNotExistError, ReceiptClosedError) as e:
            raise e

    def get_sales_report(self) -> ReportInfo:
        closed_receipts = [
            receipt
            for receipt in self.receipts.read_all()
            if receipt.status == "closed"
        ]

        total_sale_num = len(closed_receipts)

        total_revenue = sum(receipt.get_total() for receipt in closed_receipts)

        return ReportInfo(total_sale_num=total_sale_num, total_revenue=total_revenue)
