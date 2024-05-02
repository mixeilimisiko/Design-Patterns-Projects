from entities import (
    Batch,
    Item,
    ItemPack,
    NoDiscount,
    NoSellable,
    PercentageDiscount,
    PercentageDiscountStrategy,
    Receipt,
    ReceiptBuilder,
    ReceiptDiscountStrategy,
)


def test_no_discount_strategy() -> None:
    no_discount = NoDiscount()
    assert no_discount.applyDiscount(100) == 100


def test_percentage_discount_strategy() -> None:
    percentage_discount = PercentageDiscountStrategy(0.2)
    assert percentage_discount.applyDiscount(100) == 80


def test_receipt_discount_strategy_prime_customer() -> None:
    receipt_discount = ReceiptDiscountStrategy(customer_id=7, percentage=0.1)
    assert receipt_discount.applyDiscount(100) == 90


def test_receipt_discount_strategy_non_prime_customer() -> None:
    receipt_discount = ReceiptDiscountStrategy(customer_id=8, percentage=0.1)
    assert receipt_discount.applyDiscount(100) == 100


def test_item() -> None:
    item = Item(id=1, name="Milk", price=2.5)
    assert item.getId() == 1
    assert item.getName() == "Milk"
    assert item.getPrice() == 2.5


def test_batch() -> None:
    item = Item(id=1, name="Milk", price=2.5)
    batch = Batch(id=1, amount=3, item_type=item)
    assert batch.getId() == 1
    assert batch.getName() == "Milk 3 pack"
    assert batch.getPrice() == 3 * 2.5


def test_receipt() -> None:
    item = Item(id=1, name="Milk", price=2.5)
    batch = Batch(id=2, amount=3, item_type=item)
    receipt = Receipt(id=1, sellables=[item, batch])
    assert receipt.getId() == 1
    assert receipt.getName() == "Receipt 1"
    assert receipt.getPrice() == (item.getPrice() + batch.getPrice())


def test_receipt_builder() -> None:
    item = Item(id=1, name="Milk", price=2.5)
    builder = ReceiptBuilder(id=1).with_sellable(item)
    receipt = builder.build()
    assert receipt.getId() == 1
    assert receipt.getName() == "Receipt 1"
    assert receipt.getPrice() == item.getPrice()


def test_item_with_percentage_discount() -> None:
    item = Item(id=1, name="Milk", price=2.5)
    discount_strategy = PercentageDiscountStrategy(0.2)
    item.setDiscountStrategy(discount_strategy)
    assert item.getPrice() == 2.5 * 0.8


def test_item_pack_single_item_no_discount() -> None:
    item1 = Item(id=1, name="Apple", price=1.5)
    item_pack = ItemPack(id=2, sellables=[item1])

    assert item_pack.getId() == 2
    assert item_pack.getName() == "Apple 1 pack"
    assert item_pack.getPrice() == 1.5
    assert item_pack.getDiscountStrategy() == NoDiscount()


def test_item_pack_single_item_with_discount() -> None:
    item1 = Item(id=3, name="Banana", price=1.0)
    item_pack = ItemPack(id=4, sellables=[item1])

    # Applying a 20% discount on the item pack
    discount_strategy = PercentageDiscountStrategy(0.2)
    item_pack.setDiscountStrategy(discount_strategy)

    assert item_pack.getId() == 4
    assert item_pack.getName() == "Banana 1 pack"
    assert item_pack.getPrice() == 1.0 * 0.8
    assert item_pack.getDiscountStrategy() == discount_strategy


def test_item_pack_multiple_items_no_discount() -> None:
    item1 = Item(id=5, name="Orange", price=2.0)
    item2 = Item(id=6, name="Orange", price=2.5)
    item_pack = ItemPack(id=7, sellables=[item1, item2])

    assert item_pack.getId() == 7
    assert item_pack.getName() == "Orange 2 pack"
    assert item_pack.getPrice() == 2.0 + 2.5
    assert item_pack.getDiscountStrategy() == NoDiscount()


def test_item_pack_multiple_items_with_discount() -> None:
    item1 = Item(id=8, name="Cherry", price=1.0)
    item2 = Item(id=9, name="Cherry", price=1.25)
    item_pack = ItemPack(id=10, sellables=[item1, item2])

    discount_strategy = PercentageDiscountStrategy(0.15)
    item_pack.setDiscountStrategy(discount_strategy)

    assert item_pack.getId() == 10
    assert item_pack.getName() == "Cherry 2 pack"
    assert item_pack.getPrice() == 1.9125
    assert item_pack.getDiscountStrategy() == discount_strategy


def test_receipt_with_multiple_sellables_and_discounts() -> None:
    item = Item(id=1, name="Milk", price=2.5)
    batch = Batch(id=2, amount=3, item_type=item)
    discount_strategy_1 = PercentageDiscountStrategy(0.2)
    discount_strategy_2 = ReceiptDiscountStrategy(customer_id=7, percentage=0.1)
    item.setDiscountStrategy(discount_strategy_1)
    batch.setDiscountStrategy(discount_strategy_1)
    receipt = Receipt(id=1, sellables=[item, batch])
    receipt.setDiscountStrategy(discount_strategy_2)
    expected_price = (2.5 + 3 * 2.5) * 0.8 * 0.9
    assert receipt.getPrice() == expected_price


def test_receipt_builder_with_id() -> None:
    builder = ReceiptBuilder()
    result = builder.with_id(123)
    assert result.id == 123


def test_receipt_builder_with_sellable() -> None:
    builder = ReceiptBuilder()
    item = NoSellable()
    result = builder.with_sellable(item)
    assert item in result.sellables


def test_receipt_builder_with_payment_method() -> None:
    builder = ReceiptBuilder()
    result = builder.with_payment_method("cash")
    assert result.payment_method == "cash"


def test_receipt_builder_with_discount_strategy() -> None:
    builder = ReceiptBuilder()
    strategy = NoDiscount()
    result = builder.with_discount_strategy(strategy)
    assert result.discount_strategy == strategy


def test_receipt_builder_build() -> None:
    builder = ReceiptBuilder()
    result = builder.build()
    assert isinstance(result, Receipt)


def test_percentage_discount_get_id() -> None:
    discount = PercentageDiscount(id=1, item_id=2, percentage=0.1)
    result = discount.getId()
    assert result == 1


def test_percentage_discount_get_item_id() -> None:
    discount = PercentageDiscount(id=1, item_id=2, percentage=0.1)
    result = discount.getItemId()
    assert result == 2


def test_percentage_discount_get_value() -> None:
    discount = PercentageDiscount(id=1, item_id=2, percentage=0.1)
    result = discount.getValue()
    assert result == 0.1
