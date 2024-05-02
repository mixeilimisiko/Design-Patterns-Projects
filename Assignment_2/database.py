from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Protocol

from entities import Batch, Discount, Item, Sellable


class ItemRepository(Protocol):
    def create(self, sellable: Item) -> None:
        pass

    def read(self, sellable_id: int) -> Item:
        pass

    def update(self, sellable: Item) -> None:
        pass

    def delete(self, sellable_id: int) -> None:
        pass

    def get_all(self) -> List[Sellable]:
        pass


class DiscountRepository(Protocol):
    def create(self, discount: Discount) -> None:
        pass

    def read(self, discount_id: int) -> Discount:
        pass

    def update(self, discount: Discount) -> None:
        pass

    def delete(self, discount_id: int) -> None:
        pass

    def get_item_discount(self, item_id: int) -> float:
        pass

    def get_all(self) -> List[Discount]:
        pass


class BatchRepository(Protocol):
    def create(self, batch: Batch) -> None:
        pass

    def read(self, batch_id: int) -> Batch:
        pass

    def update(self, batch: Batch) -> None:
        pass

    def delete(self, batch_id: int) -> None:
        pass

    def get_all(self) -> List[Sellable]:
        pass


class ExistsError(Exception):
    pass


class DoesNotExistError(Exception):
    pass


@dataclass
class InMemoryItemRepository(ItemRepository):
    sellables: dict[int, Item] = field(default_factory=dict)

    def create(self, sellable: Item) -> None:
        if sellable.getId() in self.sellables:
            raise ExistsError

        self.sellables[sellable.getId()] = sellable

    def read(self, sellable_id: int) -> Item:
        try:
            return self.sellables[sellable_id]
        except KeyError:
            raise DoesNotExistError

    def update(self, sellable: Item) -> None:
        if sellable.getId() not in self.sellables:
            raise DoesNotExistError

        self.sellables[sellable.getId()] = sellable

    def delete(self, sellable_id: int) -> None:
        try:
            del self.sellables[sellable_id]
        except KeyError:
            raise DoesNotExistError

    def get_all(self) -> List[Sellable]:
        # Implement logic to retrieve all items
        # Example for InMemoryItemRepository:
        return list(self.sellables.values())


@dataclass
class InMemoryDiscountRepository(DiscountRepository):
    discounts: dict[int, Discount] = field(default_factory=dict)

    def create(self, discount: Discount) -> None:
        if discount.getId() in self.discounts:
            raise ExistsError

        self.discounts[discount.getId()] = discount

    def read(self, discount_id: int) -> Discount:
        try:
            return self.discounts[discount_id]
        except KeyError:
            raise DoesNotExistError

    def update(self, discount: Discount) -> None:
        if discount.getId() not in self.discounts:
            raise DoesNotExistError

        self.discounts[discount.getId()] = discount

    def delete(self, discount_id: int) -> None:
        try:
            del self.discounts[discount_id]
        except KeyError:
            raise DoesNotExistError

    def get_item_discount(self, item_id: int) -> float:
        # Search for an item-specific discount in the repository
        for discount in self.discounts.values():
            if discount.getItemId() == item_id:
                return discount.getValue()

        return 0

    def get_all(self) -> List[Discount]:
        return list(self.discounts.values())


@dataclass
class InMemoryBatchRepository(BatchRepository):
    batches: dict[int, Batch] = field(default_factory=dict)

    def create(self, batch: Batch) -> None:
        if batch.getId() in self.batches:
            raise ExistsError

        self.batches[batch.getId()] = batch

    def read(self, batch_id: int) -> Batch:
        try:
            return self.batches[batch_id]
        except KeyError:
            raise DoesNotExistError

    def update(self, batch: Batch) -> None:
        if batch.getId() not in self.batches:
            raise DoesNotExistError

        self.batches[batch.getId()] = batch

    def delete(self, batch_id: int) -> None:
        try:
            del self.batches[batch_id]
        except KeyError:
            raise DoesNotExistError

    def get_all(self) -> List[Sellable]:
        return list(self.batches.values())
