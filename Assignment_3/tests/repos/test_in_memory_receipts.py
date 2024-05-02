from uuid import UUID, uuid4

import pytest

from core.receipts import (
    Receipt,
    ReceiptClosedError,
    ReceiptDoesNotExistError,
    ReceiptExistsError,
    ReceiptProduct,
)
from infra.repos.in_memory.in_memory_products import InMemoryProducts
from infra.repos.in_memory.in_memory_receipts import InMemoryReceipts
from tests.fake_generator import FakeGenerator


@pytest.fixture
def fake_generator() -> FakeGenerator:
    return FakeGenerator()


def test_should_create_receipt(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_receipt: Receipt = Receipt()

    receipts_repository.create(fake_receipt)
    assert receipts_repository.read(fake_receipt.id) == fake_receipt


def test_should_not_create_duplicate_receipt(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_receipt1: Receipt = Receipt()
    fake_receipt2: Receipt = Receipt(id=fake_receipt1.id)

    receipts_repository.create(fake_receipt1)

    with pytest.raises(ReceiptExistsError):
        receipts_repository.create(fake_receipt2)


def test_should_add_product_to_receipt(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    products_repository: InMemoryProducts = InMemoryProducts()
    fake_receipt: Receipt = Receipt()
    fake_product: ReceiptProduct = ReceiptProduct(
        inner=fake_generator.generate_product(), quantity=2
    )

    receipts_repository.create(fake_receipt)
    products_repository.create(fake_product.inner)

    receipts_repository.add_product(fake_receipt.id, fake_product)

    retrieved_receipt: Receipt = receipts_repository.read(fake_receipt.id)
    assert retrieved_receipt.products == [fake_product]


def test_should_not_add_product_to_nonexistent_receipt(
    fake_generator: FakeGenerator,
) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_product: ReceiptProduct = ReceiptProduct(
        inner=fake_generator.generate_product(), quantity=2
    )

    with pytest.raises(ReceiptDoesNotExistError):
        receipts_repository.add_product(uuid4(), fake_product)


def test_should_not_add_product_to_closed_receipt(
    fake_generator: FakeGenerator,
) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_receipt: Receipt = Receipt(status="closed")
    fake_product: ReceiptProduct = ReceiptProduct(
        inner=fake_generator.generate_product(), quantity=2
    )

    receipts_repository.create(fake_receipt)

    with pytest.raises(ReceiptClosedError):
        receipts_repository.add_product(fake_receipt.id, fake_product)


def test_should_read_receipt(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_receipt: Receipt = Receipt()

    receipts_repository.create(fake_receipt)
    retrieved_receipt: Receipt = receipts_repository.read(fake_receipt.id)
    assert retrieved_receipt == fake_receipt


def test_should_not_read_nonexistent_receipt() -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    unknown_receipt_id: UUID = uuid4()

    with pytest.raises(ReceiptDoesNotExistError):
        receipts_repository.read(unknown_receipt_id)


def test_should_update_receipt_status(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_receipt: Receipt = Receipt()

    receipts_repository.create(fake_receipt)

    new_status: str = "closed"
    receipts_repository.update_status(fake_receipt.id, new_status)

    updated_receipt: Receipt = receipts_repository.read(fake_receipt.id)
    assert updated_receipt.status == new_status


def test_should_not_update_status_of_nonexistent_receipt() -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    unknown_receipt_id: UUID = uuid4()

    with pytest.raises(ReceiptDoesNotExistError):
        receipts_repository.update_status(unknown_receipt_id, "closed")


def test_should_not_delete_closed_receipt(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    fake_receipt: Receipt = Receipt()

    receipts_repository.create(fake_receipt)
    receipts_repository.update_status(fake_receipt.id, "closed")

    with pytest.raises(ReceiptClosedError):
        receipts_repository.delete(fake_receipt.id)


def test_should_not_delete_nonexistent_receipt() -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()
    unknown_receipt_id: UUID = uuid4()

    with pytest.raises(ReceiptDoesNotExistError):
        receipts_repository.delete(unknown_receipt_id)


def test_should_read_all_receipts(fake_generator: FakeGenerator) -> None:
    receipts_repository: InMemoryReceipts = InMemoryReceipts()

    fake_receipt1: Receipt = Receipt()
    fake_receipt2: Receipt = Receipt()
    fake_receipt3: Receipt = Receipt()

    receipts_repository.create(fake_receipt1)
    receipts_repository.create(fake_receipt2)
    receipts_repository.create(fake_receipt3)

    all_receipts = receipts_repository.read_all()

    assert len(all_receipts) == 3
    assert fake_receipt1 in all_receipts
    assert fake_receipt2 in all_receipts
    assert fake_receipt3 in all_receipts
