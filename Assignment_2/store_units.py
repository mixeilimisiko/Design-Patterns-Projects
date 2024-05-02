from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol

from database import BatchRepository, DiscountRepository, ExistsError, ItemRepository
from entities import (
    Batch,
    Item,
    NoSellable,
    PercentageDiscountStrategy,
    Receipt,
    Sellable,
)


# abstraction layer for customer
# main reason is not to give customer direct access to item repository
class Catalog(Protocol):
    def browse_catalog(self) -> List[Sellable]:
        pass

    def pick_product(self, item_id: int) -> Sellable:
        pass

    def pick_batch(self, batch_id: int) -> Sellable:
        pass


@dataclass
class NoCatalog:
    def browse_catalog(self) -> List[Sellable]:
        return []

    def pick_product(self, item_id: int) -> Sellable:
        return NoSellable()

    def pick_batch(self, batch_id: int) -> Sellable:
        return NoSellable()


@dataclass
class DefaultCatalog:
    item_repo: ItemRepository
    batch_repo: BatchRepository

    def browse_catalog(self) -> List[Sellable]:
        try:
            # Retrieve all items from the item and batch repositories
            return self.item_repo.get_all() + self.batch_repo.get_all()

        except ExistsError:
            print("Error retrieving items from the catalog.")
            return []

    def pick_product(self, item_id: int) -> Sellable:
        try:
            # Retrieve the selected item from the catalog
            selected_item = self.item_repo.read(item_id)
            return selected_item

        except ExistsError:
            print("Item not found in the catalog.")
            return NoSellable()

    def pick_batch(self, batch_id: int) -> Sellable:
        try:
            # Retrieve the selected item from the catalog
            selected_item = self.batch_repo.read(batch_id)
            return selected_item

        except ExistsError:
            print("Item not found in the catalog.")
            return NoSellable()


# abstraction layer for cashier not to use crud repositories directly
class PricingSystem(Protocol):
    def manage_discount(self, sellable: Sellable) -> Sellable:
        pass


@dataclass
class NoPricingSystem:
    def manage_discount(self, sellable: Sellable) -> Sellable:
        return sellable


@dataclass
class DefaultPricingSystem:
    discount_repository: DiscountRepository
    item_repository: ItemRepository

    def manage_discount(self, sellable: Sellable) -> Sellable:
        item_discount = 0.0
        if isinstance(sellable, Item):
            item_discount = self.discount_repository.get_item_discount(sellable.getId())
        if isinstance(sellable, Batch):
            item_discount = self.discount_repository.get_item_discount(
                sellable.item_type.getId()
            )
        if isinstance(sellable, Receipt):
            return sellable
        if item_discount != 0:
            strategy = PercentageDiscountStrategy(item_discount)
            sellable.setDiscountStrategy(strategy)
        return sellable


class CashRegister(Protocol):
    ENTRIES_FOR_X_REPORT: int = 20
    ENTRIES_FOR_Z_REPORT: int = 100

    def add_observer(self, observer: CashRegisterObserver) -> None:
        pass

    def remove_observer(self, observer: CashRegisterObserver) -> None:
        pass

    def notify_observers(self, z_report: bool = False) -> None:
        pass

    def get_transaction_cnt(self) -> int:
        pass

    def close_receipt(self, receipt: Receipt) -> None:
        pass

    def clear(self) -> None:
        pass


@dataclass
class NoCashRegister(CashRegister):
    def add_observer(self, observer: CashRegisterObserver) -> None:
        pass

    def remove_observer(self, observer: CashRegisterObserver) -> None:
        pass

    def notify_observers(self, z_report: bool = False) -> None:
        pass

    def get_transaction_cnt(self) -> int:
        return 0

    def close_receipt(self, receipt: Receipt) -> None:
        pass

    def clear(self) -> None:
        pass


@dataclass
class InMemoryCashRegister(CashRegister):
    transactions: List[Receipt] = field(default_factory=list)
    observers: List[CashRegisterObserver] = field(default_factory=list)
    transaction_cnt: int = 0

    def add_observer(self, observer: CashRegisterObserver) -> None:
        self.observers.append(observer)

    def remove_observer(self, observer: CashRegisterObserver) -> None:
        self.observers.remove(observer)

    def notify_observers(self, z_report: bool = False) -> None:
        for observer in self.observers:
            observer.update_x(self.transactions)
            if z_report:
                observer.update_z()

    def get_transaction_cnt(self) -> int:
        return self.transaction_cnt

    def close_receipt(self, receipt: Receipt) -> None:
        self.transactions.append(receipt)
        self.transaction_cnt += 1

        if self.transaction_cnt % CashRegister.ENTRIES_FOR_Z_REPORT == 0:
            self.notify_observers(z_report=True)
        elif self.transaction_cnt % CashRegister.ENTRIES_FOR_X_REPORT == 0:
            self.notify_observers()

    def clear(self) -> None:
        # Reset transactions when generating Z report
        self.transactions.clear()
        self.transaction_cnt = 0


class CashRegisterObserver(Protocol):
    def update_x(self, transactions: List[Receipt]) -> None:
        pass

    def update_z(self) -> None:
        pass
