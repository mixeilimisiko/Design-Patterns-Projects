# ===========================================================================================================#
# NoCasher Tests
# ===========================================================================================================#

from database import (
    InMemoryBatchRepository,
    InMemoryDiscountRepository,
    InMemoryItemRepository,
)
from entities import Batch, Item, NoReceipt, Receipt
from store_agents import (
    DefaultCashier,
    DefaultCustomer,
    DefaultStoreManager,
    NoCashier,
    NoCustomer,
    TestConsole,
    TransactionAnalyzer,
)
from store_units import DefaultCatalog, DefaultPricingSystem, InMemoryCashRegister


def test_no_cashier_open_receipt() -> None:
    no_cashier = NoCashier()
    no_cashier.open_receipt(1)  # Ensure the method doesn't raise an exception


def test_no_cashier_register_item() -> None:
    no_cashier = NoCashier()
    sellable = Item(id=1, name="Test Item", price=10.0)
    no_cashier.register_item(sellable)  # Ensure the method doesn't raise an exception


def test_no_cashier_show_receipt() -> None:
    no_cashier = NoCashier()
    result = no_cashier.show_receipt()
    assert isinstance(result, NoReceipt)


def test_no_cashier_close_receipt() -> None:
    no_cashier = NoCashier()
    result = no_cashier.close_receipt("cash")
    assert isinstance(result, NoReceipt)


def test_no_cashier_generate_z_report() -> None:
    no_cashier = NoCashier()
    no_cashier.generate_z_report()  # Ensure the method doesn't raise an exception


# ===========================================================================================================#
# DefaultCasher Tests
# ===========================================================================================================#


def test_default_cashier_open_receipt() -> None:
    pricing_system = DefaultPricingSystem(
        discount_repository=InMemoryDiscountRepository(),
        item_repository=InMemoryItemRepository(),
    )
    cash_register = InMemoryCashRegister()
    cashier = DefaultCashier(pricing_system=pricing_system, cash_register=cash_register)

    # Test open_receipt
    cashier.open_receipt(1)
    assert cash_register.get_transaction_cnt() == 0


def test_default_cashier_register_item() -> None:
    pricing_system = DefaultPricingSystem(
        discount_repository=InMemoryDiscountRepository(),
        item_repository=InMemoryItemRepository(),
    )
    cash_register = InMemoryCashRegister()
    cashier = DefaultCashier(pricing_system=pricing_system, cash_register=cash_register)

    # Test register_item
    sellable = Item(id=1, name="Test Item", price=10.0)
    cashier.register_item(sellable)

    # Ensure the item is added to the current receipt
    assert len(cashier.curr_receipt.sellables) == 1
    assert cashier.curr_receipt.sellables[0] == sellable


def test_default_cashier_show_receipt() -> None:
    pricing_system = DefaultPricingSystem(
        discount_repository=InMemoryDiscountRepository(),
        item_repository=InMemoryItemRepository(),
    )
    cash_register = InMemoryCashRegister()
    cashier = DefaultCashier(pricing_system=pricing_system, cash_register=cash_register)

    # Test show_receipt
    cashier.open_receipt(1)
    sellable = Item(id=1, name="Test Item", price=10.0)
    cashier.register_item(sellable)
    result = cashier.show_receipt()

    # Ensure the result is a receipt and printed
    assert isinstance(result, Receipt)
    # Add additional assertions related to printing if needed


def test_default_cashier_close_receipt() -> None:
    pricing_system = DefaultPricingSystem(
        discount_repository=InMemoryDiscountRepository(),
        item_repository=InMemoryItemRepository(),
    )
    cash_register = InMemoryCashRegister()
    cashier = DefaultCashier(pricing_system=pricing_system, cash_register=cash_register)

    # Test close_receipt
    cashier.open_receipt(1)
    sellable = Item(id=1, name="Test Item", price=10.0)
    cashier.register_item(sellable)
    result = cashier.close_receipt("cash")

    # Ensure the result is a receipt and added to the cash register
    assert isinstance(result, Receipt)
    assert cash_register.get_transaction_cnt() == 1


def test_default_cashier_generate_z_report() -> None:
    pricing_system = DefaultPricingSystem(
        discount_repository=InMemoryDiscountRepository(),
        item_repository=InMemoryItemRepository(),
    )
    cash_register = InMemoryCashRegister()
    cashier = DefaultCashier(pricing_system=pricing_system, cash_register=cash_register)

    # Test generate_z_report
    cashier.generate_z_report()

    # Ensure the cash register transactions are cleared
    assert cash_register.get_transaction_cnt() == 0


# ===========================================================================================================#
#  NoCustomer Tests
# ===========================================================================================================#


def test_no_customer_pick_specific_product() -> None:
    no_customer = NoCustomer()
    no_customer.pick_specific_product(1)  # NoCatalog, so product ID doesn't matter

    assert len(no_customer.get_cart_items()) == 0


def test_no_customer_pick_random_products() -> None:
    no_customer = NoCustomer()
    no_customer.pick_random_products(
        3
    )  # NoCatalog, so the number of products doesn't matter

    assert len(no_customer.get_cart_items()) == 0


def test_no_customer_get_cart_items() -> None:
    no_customer = NoCustomer()
    cart_items = no_customer.get_cart_items()

    assert len(cart_items) == 0


def test_no_customer_pay() -> None:
    no_customer = NoCustomer()
    payment_method = no_customer.pay(
        NoReceipt()
    )  # NoReceipt, as there are no items in the cart

    assert payment_method == ""  # Check if it's a NoReceipt


# ===========================================================================================================#
#  DefaultCustomer Tests
# ===========================================================================================================#


class CashChooser:
    def choose_payment_method(self) -> str:
        return "cash"


def test_default_customer_pick_specific_product() -> None:
    catalog = DefaultCatalog(
        item_repo=InMemoryItemRepository(), batch_repo=InMemoryBatchRepository()
    )
    item_id = 1
    catalog.item_repo.create(Item(id=item_id, name="Test Item", price=10.0))
    customer = DefaultCustomer(catalog=catalog)

    customer.pick_specific_product(item_id)

    assert len(customer.get_cart_items()) == 1
    assert customer.get_cart_items()[0].getId() == item_id


def test_default_customer_pick_random_products() -> None:
    catalog = DefaultCatalog(
        item_repo=InMemoryItemRepository(), batch_repo=InMemoryBatchRepository()
    )
    catalog.item_repo.create(Item(id=1, name="Test Item 1", price=10.0))
    catalog.item_repo.create(Item(id=2, name="Test Item 2", price=20.0))
    customer = DefaultCustomer(catalog=catalog)

    customer.pick_random_products(2)

    assert len(customer.get_cart_items()) == 2


def test_default_customer_get_cart_items() -> None:
    catalog = DefaultCatalog(
        item_repo=InMemoryItemRepository(), batch_repo=InMemoryBatchRepository()
    )
    item_id = 1
    catalog.item_repo.create(Item(id=item_id, name="Test Item", price=10.0))
    customer = DefaultCustomer(catalog=catalog)

    customer.pick_specific_product(item_id)
    cart_items = customer.get_cart_items()

    assert len(cart_items) == 1
    assert cart_items[0].getId() == item_id


def test_default_customer_pay() -> None:
    catalog = DefaultCatalog(
        item_repo=InMemoryItemRepository(), batch_repo=InMemoryBatchRepository()
    )
    item_id = 1
    catalog.item_repo.create(Item(id=item_id, name="Test Item", price=10.0))
    customer = DefaultCustomer(catalog=catalog, payment_chooser=CashChooser())

    customer.pick_specific_product(item_id)
    payment_method = customer.pay(NoReceipt())

    assert payment_method == "cash"


# ===========================================================================================================#
#  NoStoreManager Tests
# ===========================================================================================================#


# ===========================================================================================================#
#  TransactionAnalyzer Tests
# ===========================================================================================================#


def test_transaction_analyzer_analyze_transactions() -> None:
    transaction_analyzer = TransactionAnalyzer()
    transactions = [
        Receipt(
            sellables=[Item(id=1, name="Product1", price=10.0)],
            id=2,
            payment_method="cash",
        ),
        Receipt(
            sellables=[
                Batch(id=2, amount=3, item_type=Item(id=2, name="Product2", price=20.0))
            ],
            id=2,
            payment_method="cash",
        ),
        Receipt(
            sellables=[Item(id=1, name="Product1", price=10.0)],
            id=3,
            payment_method="card",
        ),
    ]

    transaction_analyzer.analyze_transactions(transactions)

    total_cash_revenue = transaction_analyzer.get_total_cash_revenue()
    total_card_revenue = transaction_analyzer.get_total_card_revenue()
    product_sales = transaction_analyzer.get_product_sales()

    assert total_cash_revenue == 70.0
    assert total_card_revenue == 10.0
    assert product_sales == {
        "Product1": 2,
        "Product2": 3,
    }


# ===========================================================================================================#
#  DefaultManager Tests
# ===========================================================================================================#
def test_store_manager_console_interaction() -> None:
    test_console = TestConsole(val=True)
    register = InMemoryCashRegister()
    cashier = DefaultCashier(cash_register=register)
    manager = DefaultStoreManager(console=test_console, cashier=cashier)

    # Add some values to CashRegister
    item = Item(id=1, name="Test Item", price=10.0)
    batch = Batch(id=2, amount=3, item_type=item)
    register.close_receipt(Receipt(sellables=[item, batch], id=1))
    manager.update_z()
    assert register.get_transaction_cnt() == 1
    assert manager.shift_cnt == 0
    manager.update_z()
    assert register.get_transaction_cnt() == 0
    assert manager.shift_cnt == 1
