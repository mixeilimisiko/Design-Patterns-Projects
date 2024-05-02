from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol, Tuple

from store_agents import (
    Cashier,
    Customer,
    DefaultCashier,
    DefaultCustomer,
    DefaultStoreManager,
    NoCashier,
    NoCustomer,
    NoStoreManager,
    StoreManager,
)
from store_units import CashRegister, Catalog, PricingSystem


class StoreAgentFactory(Protocol):
    def create_cashier_and_manager(self) -> Tuple[Cashier, StoreManager]:
        pass

    def create_customer(self) -> Customer:
        pass


@dataclass
class NoStoreAgentFactory:
    def create_cashier_and_manager(self) -> Tuple[Cashier, StoreManager]:
        return NoCashier(), NoStoreManager()

    def create_customer(self) -> Customer:
        return NoCustomer()


@dataclass
class DefaultStoreAgentFactory:
    catalog: Catalog
    cash_register: CashRegister
    pricing_system: PricingSystem

    def create_cashier_and_manager(self) -> Tuple[Cashier, StoreManager]:
        cashier = DefaultCashier(
            cash_register=self.cash_register, pricing_system=self.pricing_system
        )

        store_manager = DefaultStoreManager(cashier=cashier)
        self.cash_register.add_observer(store_manager)

        return cashier, store_manager

    def create_customer(self) -> Customer:
        customer = DefaultCustomer(catalog=self.catalog)
        num_random_products = random.randint(1, 5)
        customer.pick_random_products(num_random_products)
        return customer
