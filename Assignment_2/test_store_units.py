from dataclasses import dataclass, field
from typing import List

import pytest

from database import (
    BatchRepository,
    DoesNotExistError,
    InMemoryBatchRepository,
    InMemoryDiscountRepository,
    InMemoryItemRepository,
    ItemRepository,
)
from entities import Batch, Item, NoDiscount, NoSellable, PercentageDiscount, Receipt
from store_units import (
    CashRegister,
    CashRegisterObserver,
    DefaultCatalog,
    DefaultPricingSystem,
    InMemoryCashRegister,
    NoCatalog,
    NoPricingSystem,
)


@pytest.fixture
def item_repo() -> ItemRepository:
    return InMemoryItemRepository()


@pytest.fixture
def batch_repo() -> BatchRepository:
    return InMemoryBatchRepository()


# ===========================================================================================================#
# DefaultCatalog Tests
# ===========================================================================================================#


def test_create_and_browse_catalog(
    item_repo: ItemRepository, batch_repo: BatchRepository
) -> None:
    catalog = DefaultCatalog(item_repo=item_repo, batch_repo=batch_repo)

    # Create items
    milk = Item(id=1, name="Milk", price=2.99)
    bread = Item(id=2, name="Bread", price=1.99)

    # Create batches
    water_batch = Batch(id=3, amount=6, item_type=milk)

    # Add items and batches to repositories
    item_repo.create(milk)
    item_repo.create(bread)
    batch_repo.create(water_batch)

    # Test browse catalog
    catalog_items = catalog.browse_catalog()
    assert len(catalog_items) == 3  # 2 items + 1 batch


def test_pick_product(item_repo: ItemRepository, batch_repo: BatchRepository) -> None:
    catalog = DefaultCatalog(item_repo=item_repo, batch_repo=batch_repo)

    # Create items
    milk = Item(id=1, name="Milk", price=2.99)
    bread = Item(id=2, name="Bread", price=1.99)

    # Add items to repository
    item_repo.create(milk)
    item_repo.create(bread)

    # Test pick product
    selected_milk = catalog.pick_product(1)
    selected_bread = catalog.pick_product(2)

    assert selected_milk.getName() == "Milk"
    assert selected_bread.getName() == "Bread"


def test_pick_product_not_found(
    item_repo: ItemRepository, batch_repo: BatchRepository
) -> None:
    catalog = DefaultCatalog(item_repo=item_repo, batch_repo=batch_repo)

    # Test pick product with non-existent ID
    with pytest.raises(DoesNotExistError):
        catalog.pick_product(1)


def test_pick_batch(item_repo: ItemRepository, batch_repo: BatchRepository) -> None:
    catalog = DefaultCatalog(item_repo=item_repo, batch_repo=batch_repo)

    # Create items
    milk = Item(id=1, name="Milk", price=2.99)
    water_batch = Batch(id=3, amount=6, item_type=milk)

    # Add items and batches to repositories
    item_repo.create(milk)
    batch_repo.create(water_batch)

    # Test pick batch
    selected_batch = catalog.pick_batch(3)

    assert selected_batch.getName() == "Milk 6 pack"


def test_browse_empty_catalog() -> None:
    catalog = DefaultCatalog(
        item_repo=InMemoryItemRepository(), batch_repo=InMemoryBatchRepository()
    )

    # Test browse catalog when empty
    catalog_items = catalog.browse_catalog()
    assert len(catalog_items) == 0


def test_browse_catalog_with_items_and_batches(
    item_repo: ItemRepository, batch_repo: BatchRepository
) -> None:
    catalog = DefaultCatalog(item_repo=item_repo, batch_repo=batch_repo)

    # Create items
    milk = Item(id=1, name="Milk", price=2.99)
    bread = Item(id=2, name="Bread", price=1.99)

    # Create batches
    water_batch = Batch(id=3, amount=6, item_type=milk)

    item_repo.create(milk)
    item_repo.create(bread)
    batch_repo.create(water_batch)

    catalog_items = catalog.browse_catalog()

    assert len(catalog_items) == 3
    assert milk in catalog_items
    assert bread in catalog_items
    assert water_batch in catalog_items


def test_browse_catalog_with_empty_repositories() -> None:
    catalog = DefaultCatalog(
        item_repo=InMemoryItemRepository(), batch_repo=InMemoryBatchRepository()
    )

    catalog_items = catalog.browse_catalog()
    assert len(catalog_items) == 0


def test_browse_catalog_with_empty_item_repository(batch_repo: BatchRepository) -> None:
    catalog = DefaultCatalog(item_repo=InMemoryItemRepository(), batch_repo=batch_repo)
    empty = Item(id=-1, name="", price=-1)
    water_batch = Batch(id=3, amount=6, item_type=empty)
    batch_repo.create(water_batch)

    catalog_items = catalog.browse_catalog()
    assert len(catalog_items) == 1


def test_browse_catalog_with_empty_batch_repository(item_repo: ItemRepository) -> None:
    catalog = DefaultCatalog(item_repo=item_repo, batch_repo=InMemoryBatchRepository())

    milk = Item(id=1, name="Milk", price=2.99)
    item_repo.create(milk)

    catalog_items = catalog.browse_catalog()
    assert len(catalog_items) == 1


def test_browse_catalog_error_handling(
    item_repo: ItemRepository, batch_repo: BatchRepository
) -> None:
    item_repo_empty = InMemoryItemRepository()
    batch_repo_empty = InMemoryBatchRepository()

    catalog = DefaultCatalog(item_repo=item_repo_empty, batch_repo=batch_repo_empty)
    catalog_items = catalog.browse_catalog()
    assert len(catalog_items) == 0


# ===========================================================================================================#
# NoCatalog Tests
# ===========================================================================================================#
def test_no_catalog_browse_catalog() -> None:
    no_catalog = NoCatalog()

    # Test browse catalog when there is no catalog (empty catalog)
    catalog_items = no_catalog.browse_catalog()
    assert len(catalog_items) == 0


def test_no_catalog_pick_product() -> None:
    no_catalog = NoCatalog()

    # Test pick_product when there is no catalog (empty catalog)
    selected_item = no_catalog.pick_product(item_id=1)
    assert isinstance(selected_item, NoSellable)


def test_no_catalog_pick_batch() -> None:
    no_catalog = NoCatalog()

    # Test pick_batch when there is no catalog (empty catalog)
    selected_item = no_catalog.pick_batch(batch_id=1)
    assert isinstance(selected_item, NoSellable)


# ===========================================================================================================#
# PricingSystem Tests
# ===========================================================================================================#


def test_no_pricing_system_manage_discount() -> None:
    no_pricing_system = NoPricingSystem()

    # Test manage_discount when there is no pricing system (no discount applied)
    item = Item(id=1, name="Test Item", price=10.0)
    result_item = no_pricing_system.manage_discount(item)
    assert result_item.getPrice() == item.getPrice()
    assert isinstance(result_item.getDiscountStrategy(), NoDiscount)

    batch = Batch(id=2, amount=3, item_type=item)
    result_batch = no_pricing_system.manage_discount(batch)
    assert result_batch.getPrice() == batch.getPrice()
    assert isinstance(result_batch.getDiscountStrategy(), NoDiscount)


def test_default_pricing_system_manage_discount() -> None:
    # Mock repositories
    item_repository = InMemoryItemRepository()
    discount_repository = InMemoryDiscountRepository()

    default_pricing_system = DefaultPricingSystem(
        discount_repository=discount_repository, item_repository=item_repository
    )

    # Populate repositories
    item = Item(id=1, name="Test Item", price=10.0)
    discount_repository.create(PercentageDiscount(id=1, item_id=1, percentage=0.1))

    batch = Batch(id=2, amount=3, item_type=item)
    # discount_repository.create(PercentageDiscount(id=2, item_id=1, percentage=0.2))

    # Test manage_discount with the default pricing system
    result_item = default_pricing_system.manage_discount(item)
    assert result_item.getPrice() == 9.0  # 10.0 - 10.0 * 0.1

    result_batch = default_pricing_system.manage_discount(batch)
    assert result_batch.getPrice() == 27  # 30.0 - 30.0 * 0.1


def test_default_pricing_system_manage_discount_no_discount() -> None:
    # Test manage_discount with the default pricing system when there is no discount
    item_repository = InMemoryItemRepository()
    discount_repository = InMemoryDiscountRepository()

    default_pricing_system = DefaultPricingSystem(
        discount_repository=discount_repository, item_repository=item_repository
    )

    item = Item(id=1, name="Test Item", price=10.0)
    result_item = default_pricing_system.manage_discount(item)

    assert result_item.getPrice() == 10.0
    assert isinstance(result_item.getDiscountStrategy(), NoDiscount)


# ===========================================================================================================#
# NoPricingSystem Tests
# ===========================================================================================================#


def test_no_pricing_system_manage_discount_item() -> None:
    # Test manage_discount with the NoPricingSystem for an item
    no_pricing_system = NoPricingSystem()

    item = Item(id=1, name="Test Item", price=10.0)

    result_item = no_pricing_system.manage_discount(item)
    assert result_item.getPrice() == 10.0  # No discount applied
    assert isinstance(result_item.getDiscountStrategy(), NoDiscount)


def test_no_pricing_system_manage_discount_batch() -> None:
    # Test manage_discount with the NoPricingSystem for a batch
    no_pricing_system = NoPricingSystem()

    item = Item(id=1, name="Test Item", price=10.0)
    batch = Batch(id=2, amount=3, item_type=item)

    result_batch = no_pricing_system.manage_discount(batch)
    assert result_batch.getPrice() == 30.0  # No discount applied
    assert isinstance(result_batch.getDiscountStrategy(), NoDiscount)


def test_no_pricing_system_manage_discount_receipt() -> None:
    # Test manage_discount with the NoPricingSystem for a receipt
    no_pricing_system = NoPricingSystem()

    item = Item(id=1, name="Test Item", price=10.0)
    batch = Batch(id=2, amount=3, item_type=item)
    receipt = Receipt(id=3, sellables=[item, batch])

    result_receipt = no_pricing_system.manage_discount(receipt)
    assert result_receipt.getPrice() == 40.0  # No discount applied
    assert isinstance(result_receipt.getDiscountStrategy(), NoDiscount)


# ===========================================================================================================#
# CashRegister Tests
# ===========================================================================================================#


def test_in_memory_cash_register_add_observer() -> None:
    # Test adding observer to InMemoryCashRegister
    cash_register = InMemoryCashRegister()
    observer = MockCashRegisterObserver()

    cash_register.add_observer(observer)

    assert observer in cash_register.observers


def test_in_memory_cash_register_remove_observer() -> None:
    # Test removing observer from InMemoryCashRegister
    cash_register = InMemoryCashRegister()
    observer = MockCashRegisterObserver()
    cash_register.add_observer(observer)

    cash_register.remove_observer(observer)

    assert observer not in cash_register.observers


def test_in_memory_cash_register_get_transaction_cnt() -> None:
    # Test getting transaction count from InMemoryCashRegister
    cash_register = InMemoryCashRegister()

    assert cash_register.get_transaction_cnt() == 0

    receipt = Receipt(id=1, sellables=[Item(id=1, name="Test Item", price=10.0)])
    cash_register.close_receipt(receipt)

    assert cash_register.get_transaction_cnt() == 1


def test_in_memory_cash_register_clear() -> None:
    # Test clearing transactions from InMemoryCashRegister
    cash_register = InMemoryCashRegister()

    receipt = Receipt(id=1, sellables=[Item(id=1, name="Test Item", price=10.0)])
    cash_register.close_receipt(receipt)

    assert cash_register.transactions
    assert cash_register.get_transaction_cnt() > 0

    cash_register.clear()

    assert not cash_register.transactions
    assert cash_register.get_transaction_cnt() == 0


def test_in_memory_cash_register_notify_observers_x_report() -> None:
    # Test notifying observers with X report from InMemoryCashRegister
    cash_register = InMemoryCashRegister()
    observer = MockCashRegisterObserver()
    cash_register.add_observer(observer)
    receipt = Receipt(id=1, sellables=[Item(id=1, name="Test Item", price=10.0)])

    for _ in range(CashRegister.ENTRIES_FOR_X_REPORT):
        cash_register.close_receipt(receipt)

    assert observer.transactions == cash_register.transactions
    assert observer.z_report_called == 0


def test_in_memory_cash_register_notify_observers_z_report() -> None:
    # Test notifying observers with Z report from InMemoryCashRegister
    cash_register = InMemoryCashRegister()
    observer = MockCashRegisterObserver()
    cash_register.add_observer(observer)

    for _ in range(CashRegister.ENTRIES_FOR_Z_REPORT):
        receipt = Receipt(id=1, sellables=[Item(id=1, name="Test Item", price=10.0)])
        cash_register.close_receipt(receipt)

    assert observer.transactions == cash_register.transactions
    m = observer.z_report_called
    assert m == 1


@dataclass
class MockCashRegisterObserver(CashRegisterObserver):
    z_report_called: int = 0
    transactions: List[Receipt] = field(default_factory=list)

    def update_x(self, transactions: List[Receipt]) -> None:
        self.transactions = transactions

    def update_z(self) -> None:
        self.z_report_called = 1
