import pytest

from database import (
    BatchRepository,
    DiscountRepository,
    DoesNotExistError,
    ExistsError,
    InMemoryBatchRepository,
    InMemoryDiscountRepository,
    InMemoryItemRepository,
    ItemRepository,
)
from entities import Batch, Item, PercentageDiscount


@pytest.fixture
def in_memory_item_repository() -> ItemRepository:
    return InMemoryItemRepository()


@pytest.fixture
def in_memory_discount_repository() -> DiscountRepository:
    return InMemoryDiscountRepository()


@pytest.fixture
def in_memory_batch_repository() -> BatchRepository:
    return InMemoryBatchRepository()


def test_in_memory_item_repository_should_not_read_unknown(
    in_memory_item_repository: ItemRepository,
) -> None:
    with pytest.raises(DoesNotExistError):
        in_memory_item_repository.read(1)


def test_in_memory_item_repository_should_persist(
    in_memory_item_repository: ItemRepository,
) -> None:
    item = Item(id=1, name="TestItem", price=10.0)

    in_memory_item_repository.create(item)
    retrieved_item = in_memory_item_repository.read(1)

    assert retrieved_item == item


def test_in_memory_item_repository_should_not_duplicate(
    in_memory_item_repository: ItemRepository,
) -> None:
    item = Item(id=1, name="TestItem", price=10.0)

    in_memory_item_repository.create(item)
    with pytest.raises(ExistsError):
        in_memory_item_repository.create(item)


def test_in_memory_item_repository_should_not_update_unknown(
    in_memory_item_repository: ItemRepository,
) -> None:
    item = Item(id=1, name="TestItem", price=10.0)

    with pytest.raises(DoesNotExistError):
        in_memory_item_repository.update(item)


def test_in_memory_item_repository_should_persist_update(
    in_memory_item_repository: ItemRepository,
) -> None:
    item = Item(id=1, name="TestItem", price=10.0)

    in_memory_item_repository.create(item)
    item.name = "UpdatedItem"
    in_memory_item_repository.update(item)
    updated_item = in_memory_item_repository.read(1)

    assert updated_item.getName() == "UpdatedItem"


def test_in_memory_item_repository_should_not_delete_unknown(
    in_memory_item_repository: ItemRepository,
) -> None:
    with pytest.raises(DoesNotExistError):
        in_memory_item_repository.delete(1)


def test_in_memory_item_repository_should_delete(
    in_memory_item_repository: ItemRepository,
) -> None:
    item = Item(id=1, name="TestItem", price=10.0)

    in_memory_item_repository.create(item)
    in_memory_item_repository.delete(1)

    with pytest.raises(DoesNotExistError):
        in_memory_item_repository.read(1)


def test_in_memory_discount_repository_should_not_read_unknown(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    with pytest.raises(DoesNotExistError):
        in_memory_discount_repository.read(1)


def test_in_memory_discount_repository_should_persist(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    discount = PercentageDiscount(id=1, item_id=1, percentage=0.1)

    in_memory_discount_repository.create(discount)
    retrieved_discount = in_memory_discount_repository.read(1)

    assert retrieved_discount == discount


def test_in_memory_discount_repository_should_not_duplicate(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    discount = PercentageDiscount(id=1, item_id=1, percentage=0.1)

    in_memory_discount_repository.create(discount)
    with pytest.raises(ExistsError):
        in_memory_discount_repository.create(discount)


def test_in_memory_discount_repository_should_not_update_unknown(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    discount = PercentageDiscount(id=1, item_id=1, percentage=0.1)

    with pytest.raises(DoesNotExistError):
        in_memory_discount_repository.update(discount)


def test_in_memory_discount_repository_should_persist_update(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    discount = PercentageDiscount(id=1, item_id=1, percentage=0.1)

    in_memory_discount_repository.create(discount)
    discount.percentage = 0.2
    in_memory_discount_repository.update(discount)
    updated_discount = in_memory_discount_repository.read(1)

    assert updated_discount.getValue() == 0.2


def test_in_memory_discount_repository_should_not_delete_unknown(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    with pytest.raises(DoesNotExistError):
        in_memory_discount_repository.delete(1)


def test_in_memory_discount_repository_should_delete(
    in_memory_discount_repository: DiscountRepository,
) -> None:
    discount = PercentageDiscount(id=1, item_id=1, percentage=0.1)

    in_memory_discount_repository.create(discount)
    in_memory_discount_repository.delete(1)

    with pytest.raises(DoesNotExistError):
        in_memory_discount_repository.read(1)


def test_in_memory_batch_repository_should_not_read_unknown(
    in_memory_batch_repository: BatchRepository,
) -> None:
    with pytest.raises(DoesNotExistError):
        in_memory_batch_repository.read(1)


def test_in_memory_batch_repository_should_persist(
    in_memory_batch_repository: BatchRepository,
) -> None:
    item_type = Item(id=1, name="TestItem", price=10.0)
    batch = Batch(id=1, amount=5, item_type=item_type)

    in_memory_batch_repository.create(batch)
    retrieved_batch = in_memory_batch_repository.read(1)

    assert retrieved_batch == batch


def test_in_memory_batch_repository_should_not_duplicate(
    in_memory_batch_repository: BatchRepository,
) -> None:
    item_type = Item(id=1, name="TestItem", price=10.0)
    batch = Batch(id=1, amount=5, item_type=item_type)

    in_memory_batch_repository.create(batch)
    with pytest.raises(ExistsError):
        in_memory_batch_repository.create(batch)


def test_in_memory_batch_repository_should_not_update_unknown(
    in_memory_batch_repository: BatchRepository,
) -> None:
    item_type = Item(id=1, name="TestItem", price=10.0)
    batch = Batch(id=1, amount=5, item_type=item_type)

    with pytest.raises(DoesNotExistError):
        in_memory_batch_repository.update(batch)


def test_in_memory_batch_repository_should_persist_update(
    in_memory_batch_repository: BatchRepository,
) -> None:
    item_type = Item(id=1, name="TestItem", price=10.0)
    batch = Batch(id=1, amount=5, item_type=item_type)

    in_memory_batch_repository.create(batch)
    batch.amount = 10
    in_memory_batch_repository.update(batch)
    updated_batch = in_memory_batch_repository.read(1)

    assert updated_batch.amount == 10


def test_in_memory_batch_repository_should_not_delete_unknown(
    in_memory_batch_repository: BatchRepository,
) -> None:
    with pytest.raises(DoesNotExistError):
        in_memory_batch_repository.delete(1)


def test_in_memory_batch_repository_should_delete(
    in_memory_batch_repository: BatchRepository,
) -> None:
    item_type = Item(id=1, name="TestItem", price=10.0)
    batch = Batch(id=1, amount=5, item_type=item_type)

    in_memory_batch_repository.create(batch)
    in_memory_batch_repository.delete(1)

    with pytest.raises(DoesNotExistError):
        in_memory_batch_repository.read(1)
