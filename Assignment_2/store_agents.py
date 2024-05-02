from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Protocol

from entities import (
    Batch,
    NoReceipt,
    Receipt,
    ReceiptBuilder,
    ReceiptDiscountStrategy,
    Sellable,
)
from printer import Printer
from store_units import (
    CashRegister,
    Catalog,
    NoCashRegister,
    NoCatalog,
    NoPricingSystem,
    PricingSystem,
)


# can have sellable factory for real database crud repositories
class Cashier(Protocol):
    def open_receipt(self, customer_number: int) -> None:
        pass

    def register_item(self, sellable: Sellable) -> None:
        pass

    def show_receipt(self) -> Receipt:
        pass

    def close_receipt(self, payment_method: str) -> Receipt:
        pass

    def generate_z_report(self) -> None:
        pass


@dataclass
class NoCashier:
    def open_receipt(self, customer_number: int) -> None:
        pass

    def register_item(self, sellable: Sellable) -> None:
        pass

    def show_receipt(self) -> Receipt:
        return NoReceipt()

    def close_receipt(self, payment_method: str) -> Receipt:
        return NoReceipt()

    def generate_z_report(self) -> None:
        pass


@dataclass
class DefaultCashier:
    cash_register: CashRegister = field(default_factory=NoCashRegister)
    pricing_system: PricingSystem = field(default_factory=NoPricingSystem)
    curr_receipt: ReceiptBuilder = field(default_factory=ReceiptBuilder)

    def open_receipt(self, customer_number: int) -> None:
        strategy = ReceiptDiscountStrategy(customer_number)
        self.curr_receipt = (
            ReceiptBuilder()
            .with_discount_strategy(strategy)
            .with_id(self.cash_register.get_transaction_cnt())
        )

    def register_item(self, sellable: Sellable) -> None:
        discounted_sellable = self.pricing_system.manage_discount(sellable)

        self.curr_receipt.with_sellable(discounted_sellable)

    def show_receipt(self) -> Receipt:
        receipt = self.curr_receipt.build()
        Printer.print_receipt(receipt)
        return receipt

    def close_receipt(self, payment_method: str) -> Receipt:
        receipt = self.curr_receipt.with_payment_method(payment_method).build()
        self.cash_register.close_receipt(receipt)
        return receipt

    def generate_z_report(self) -> None:
        self.cash_register.clear()


class PaymentChooser(Protocol):
    def choose_payment_method(self) -> str:
        pass


class RandomPaymentChooser:
    def choose_payment_method(self) -> str:
        payment_methods = ["cash", "card"]
        return random.choice(payment_methods)


class Customer(Protocol):
    def pick_specific_product(self, item_num: int) -> None:
        pass

    def pick_random_products(self, num_items: int) -> None:
        pass

    def get_cart_items(self) -> List[Sellable]:
        pass

    def pay(self, receipt: Receipt) -> str:
        pass

    def get_customer_number(self) -> int:
        pass

    def set_customer_number(self, num: int) -> None:
        pass


@dataclass
class NoCustomer:
    def pick_specific_product(self, item_num: int) -> None:
        pass

    def pick_random_products(self, num_items: int) -> None:
        pass

    def get_cart_items(self) -> List[Sellable]:
        return []

    def pay(self, receipt: Receipt) -> str:
        return ""

    def get_customer_number(self) -> int:
        return 0

    def set_customer_number(self, num: int) -> None:
        pass


@dataclass
class DefaultCustomer:
    customer_number: int = 0
    catalog: Catalog = field(default_factory=NoCatalog)
    cart: List[Sellable] = field(default_factory=list)
    payment_chooser: PaymentChooser = field(default_factory=RandomPaymentChooser)

    def pick_specific_product(self, item_num: int) -> None:
        # Pick a specific item from the catalog and add it to the cart
        selected_item = self.catalog.pick_product(item_num)
        if selected_item:
            self.cart.append(selected_item)

    def pick_random_products(self, num_items: int) -> None:
        # Pick a random combination of items from the catalog and add them to the cart
        catalog_items = self.catalog.browse_catalog()
        if catalog_items:
            # random_items = sample(catalog_items, min(num_items, len(catalog_items)))
            random_items = random.choices(catalog_items, k=num_items)
            self.cart.extend(random_items)

    def get_cart_items(self) -> List[Sellable]:
        # print("Items in the cart:")
        # for item in self.cart:
        #     print(f"Product: {item.getName()}, Price: {item.getPrice()}")
        return self.cart

    def pay(self, receipt: Receipt) -> str:
        return self.payment_chooser.choose_payment_method()

    def get_customer_number(self) -> int:
        return self.customer_number

    def set_customer_number(self, num: int) -> None:
        self.customer_number = num


class StoreManager(Protocol):
    def update_x(self, transactions: List[Receipt]) -> None:
        pass

    def update_z(self) -> None:
        pass

    def generate_x_report(self, transactions: List[Receipt]) -> None:
        pass

    def get_shift_num(self) -> int:
        pass


@dataclass
class NoStoreManager:
    def update_x(self, transactions: List[Receipt]) -> None:
        pass

    def update_z(self) -> None:
        pass

    def generate_x_report(self, transactions: List[Receipt]) -> None:
        pass

    def get_shift_num(self) -> int:
        return 0


class Console(Protocol):
    def read_bool(self, prompt: str) -> bool:
        pass


@dataclass
class TestConsole:
    val: bool = False

    def read_bool(self, prompt: str) -> bool:
        self.val ^= True  # XOR self.val with True
        return self.val


class RealConsole:
    def read_bool(self, prompt: str) -> bool:
        response = input(prompt + "Enter 'y' or 'n': ").lower()
        return response == "y"


@dataclass
class TransactionAnalyzer:
    total_cash_revenue: float = 0.0
    total_card_revenue: float = 0.0
    product_sales: Dict[str, int] = field(default_factory=dict)

    def analyze_transactions(self, transactions: List[Receipt]) -> None:
        self.total_cash_revenue = 0.0
        self.total_card_revenue = 0.0
        self.product_sales = {}
        for transaction in transactions:
            payment_method = transaction.get_payment_method()
            total_price = transaction.getPrice()

            if payment_method == "cash":
                self.total_cash_revenue += total_price
            elif payment_method == "card":
                self.total_card_revenue += total_price

            for sellable in transaction.sellables:
                self._update_product_sales(sellable)

    def _update_product_sales(self, sellable: Sellable) -> None:
        product_name = sellable.getName()
        units_sold = 1

        if isinstance(sellable, Batch):
            product_name = sellable.item_type.getName()
            units_sold = sellable.amount

        self.product_sales[product_name] = (
            self.product_sales.get(product_name, 0) + units_sold
        )

    def get_total_cash_revenue(self) -> float:
        return self.total_cash_revenue

    def get_total_card_revenue(self) -> float:
        return self.total_card_revenue

    def get_product_sales(self) -> Dict[str, int]:
        return self.product_sales


@dataclass
class DefaultStoreManager:
    transaction_analyzer: TransactionAnalyzer = field(
        default_factory=TransactionAnalyzer
    )
    console: Console = field(default_factory=RealConsole)
    shift_cnt: int = 0
    cashier: Cashier = field(default_factory=NoCashier)

    def update_x(self, transactions: List[Receipt]) -> None:
        # Update records and generate X report when notified about a new transaction
        if self.console.read_bool("Make x_report? \n"):
            self.generate_x_report(transactions)

    def update_z(self) -> None:
        if self.console.read_bool("End Shift? \n"):
            self.shift_cnt += 1
            self.cashier.generate_z_report()

    def generate_x_report(self, transactions: List[Receipt]) -> None:
        # Generate X report based on transactions
        # self.transaction_analyzer.set_transactions(transactions)
        self.transaction_analyzer.analyze_transactions(transactions)
        Printer.print_x_report(
            self.transaction_analyzer.get_total_cash_revenue(),
            self.transaction_analyzer.get_total_card_revenue(),
            self.transaction_analyzer.get_product_sales(),
        )

    def get_shift_num(self) -> int:
        return self.shift_cnt
