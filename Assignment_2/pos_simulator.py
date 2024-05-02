from __future__ import annotations

from dataclasses import dataclass, field

from database import BatchRepository, DiscountRepository, ItemRepository
from db_init import BatchRepositoryInitializer, DiscountInitializer, ItemInitializer
from real_database import SQLiteDBCreator
from store_agent_factory import (
    DefaultStoreAgentFactory,
    NoStoreAgentFactory,
    StoreAgentFactory,
)
from store_agents import Cashier, NoCashier, NoStoreManager, StoreManager
from store_unit_factory import (
    DefaultStoreComponentFactory,
    NoComponentFactory,
    StoreComponentFactory,
)
from store_units import (
    CashRegister,
    Catalog,
    NoCashRegister,
    NoCatalog,
    NoPricingSystem,
    PricingSystem,
)


@dataclass
class PosSimulator:
    item_repo: ItemRepository
    discount_repo: DiscountRepository
    batch_repo: BatchRepository
    component_factory: StoreComponentFactory = field(default_factory=NoComponentFactory)
    store_agent_factory: StoreAgentFactory = field(default_factory=NoStoreAgentFactory)
    catalog: Catalog = field(default_factory=NoCatalog)
    cash_register: CashRegister = field(default_factory=NoCashRegister)
    pricing_system: PricingSystem = field(default_factory=NoPricingSystem)
    cashier: Cashier = field(default_factory=NoCashier)
    store_manager: StoreManager = field(default_factory=NoStoreManager)
    # reason why customer cnt is simulator field and not customer field
    # is because customer does not need to know his/her number
    customer_cnt: int = 0

    def setup(self) -> None:
        self.component_factory = DefaultStoreComponentFactory(
            self.item_repo, self.discount_repo, self.batch_repo
        )
        self.cash_register = self.component_factory.create_cash_register()
        self.catalog = self.component_factory.create_catalog()
        self.pricing_system = self.component_factory.create_pricing_system()
        self.store_agent_factory = DefaultStoreAgentFactory(
            self.catalog, self.cash_register, self.pricing_system
        )
        (
            self.cashier,
            self.store_manager,
        ) = self.store_agent_factory.create_cashier_and_manager()
        self.customer_cnt = 0

    def simulate(self) -> None:
        while self.store_manager.get_shift_num() < 4:
            customer = self.store_agent_factory.create_customer()
            self.customer_cnt += 1
            self.cashier.open_receipt(self.customer_cnt)
            for product in customer.get_cart_items():
                self.cashier.register_item(product)
            receipt = self.cashier.show_receipt()
            payment_method = customer.pay(receipt)
            self.cashier.close_receipt(payment_method)


if __name__ == "__main__":

    db_creator = SQLiteDBCreator()
    db_creator.drop_tables()
    db_creator.create_tables()
    item_repo = ItemInitializer.initialize_item_repository(inmemory=False)
    batch_repo = BatchRepositoryInitializer.initialize_batch_repository(item_repo, inmemory=False)
    discount_repo = DiscountInitializer.initialize_discount_repository(inmemory=False)
    simulator = PosSimulator(item_repo, discount_repo, batch_repo)
    simulator.setup()
    simulator.simulate()
