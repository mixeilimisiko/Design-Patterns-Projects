from copy import deepcopy
from dataclasses import dataclass, field
from uuid import UUID

from core.receipts import (
    Receipt,
    ReceiptClosedError,
    ReceiptDoesNotExistError,
    ReceiptExistsError,
    ReceiptProduct,
)


# receipt_items: dict[tuple[UUID, UUID], int] = field(default_factory=dict)
@dataclass
class InMemoryReceipts:
    receipts: dict[UUID, Receipt] = field(default_factory=dict)

    def create(self, receipt: Receipt) -> None:
        if receipt.id in self.receipts:
            raise ReceiptExistsError(f"Receipt with id '{receipt.id}' already exists")

        self.receipts[receipt.id] = receipt

    def add_product(self, receipt_id: UUID, product: ReceiptProduct) -> None:
        if receipt_id not in self.receipts:
            raise ReceiptDoesNotExistError(
                f"Receipt with id '{receipt_id}' does not exist"
            )
        receipt = self.read(receipt_id)
        if receipt.status == "closed":
            raise ReceiptClosedError(f"Receipt with id '{receipt_id}' is closed")
        for existing_product in receipt.products:
            if existing_product.inner.id == product.inner.id:
                existing_product.quantity += product.quantity
                self.receipts[receipt.id] = receipt
                return  # Exit the function after updating quantity

        # If the product with the same ID is not found, add the new product
        self.receipts[receipt_id].add_product(deepcopy(product))

    def read(self, receipt_id: UUID) -> Receipt:
        if receipt_id not in self.receipts:
            raise ReceiptDoesNotExistError(
                f"Receipt with id '{receipt_id}' does not exist"
            )

        receipt_copy = deepcopy(self.receipts[receipt_id])
        return receipt_copy

    def update_status(self, receipt_id: UUID, receipt_status: str) -> None:
        if receipt_id not in self.receipts:
            raise ReceiptDoesNotExistError(
                f"Receipt with id '{receipt_id}' does not exist"
            )

        self.receipts[receipt_id].status = receipt_status

    def delete(self, receipt_id: UUID) -> None:
        if receipt_id not in self.receipts:
            raise ReceiptDoesNotExistError(
                f"Receipt with id '{receipt_id}' does not exist"
            )

        if self.receipts[receipt_id].status == "closed":
            raise ReceiptClosedError(f"Receipt with id '{receipt_id}' is closed")

        del self.receipts[receipt_id]

    def read_all(self) -> list[Receipt]:
        return list(self.receipts.values())
