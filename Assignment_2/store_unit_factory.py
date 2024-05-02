from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from database import BatchRepository, DiscountRepository, ItemRepository
from store_units import (
    CashRegister,
    Catalog,
    DefaultCatalog,
    DefaultPricingSystem,
    InMemoryCashRegister,
    NoCashRegister,
    NoCatalog,
    NoPricingSystem,
    PricingSystem,
)


class StoreComponentFactory(Protocol):
    def create_cash_register(self) -> CashRegister:
        pass

    def create_pricing_system(self) -> PricingSystem:
        pass

    def create_catalog(self) -> Catalog:
        pass


@dataclass
class DefaultStoreComponentFactory(StoreComponentFactory):
    item_repo: ItemRepository
    discount_repo: DiscountRepository
    batch_repo: BatchRepository

    def create_cash_register(self) -> CashRegister:
        return InMemoryCashRegister()

    def create_pricing_system(self) -> PricingSystem:
        return DefaultPricingSystem(self.discount_repo, self.item_repo)

    def create_catalog(self) -> Catalog:
        return DefaultCatalog(self.item_repo, self.batch_repo)


@dataclass
class NoComponentFactory(StoreComponentFactory):
    def create_cash_register(self) -> CashRegister:
        return NoCashRegister()

    def create_pricing_system(self) -> PricingSystem:
        return NoPricingSystem()

    def create_catalog(self) -> Catalog:
        return NoCatalog()
