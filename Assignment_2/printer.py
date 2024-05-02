from typing import Dict

from database import BatchRepository, DiscountRepository, ItemRepository
from entities import (
    Batch,
    Item,
    PercentageDiscount,
    PercentageDiscountStrategy,
    Receipt,
)


class Printer:
    @staticmethod
    def print_receipt(receipt: Receipt) -> None:
        print()
        print(
            "{:<15} | {:<7} | {:<7} | {:<8}".format(
                "Product", "Units", "Price", "Total"
            )
        )
        print("-" * 45)
        # es ar chavtvale sakmarisad mdzime logikad rom sadme sxvagan gametana ravi
        for sellable in receipt.sellables:
            product_name = sellable.getName()
            # If the sellable is a batch, get the item type name and amount
            price = sellable.getPrice()
            total = price
            units = 1
            if isinstance(sellable, Batch):
                product_name = sellable.item_type.getName()
                price = sellable.item_type.getPrice()
                units = sellable.amount
                total = sellable.getPrice()

            print(
                "{:<15} | {:<7} | ${:<6.2f} | ${:<7.2f}".format(
                    product_name, units, price, total
                )
            )

        print("-" * 45)
        print("{:<30} ${:<7.2f}".format("Total", receipt.getPrice()))
        print()
        pass

    @staticmethod
    def print_x_report(
        cash_revenue: float, card_revenue: float, product_sales: Dict[str, int]
    ) -> None:
        print("{:<15} | {:<10}".format("Product", "Units Sold"))
        print("-" * 25)

        for product, units_sold in product_sales.items():
            print("{:<15} | {:<10}".format(product, units_sold))

        print("-" * 25)
        print("{:<15} ${:<10.2f}".format("Cash Revenue", cash_revenue))
        print("{:<15} ${:<10.2f}".format("Card Revenue", card_revenue))

    @staticmethod
    def print_items(item_repo: ItemRepository) -> None:
        print("Items:")
        for item in item_repo.get_all():
            print(
                f"ID: {item.getId()}, Name: {item.getName()}, Price: {item.getPrice()}"
            )
        print("-" * 50)

    @staticmethod
    def print_batches(batch_repo: BatchRepository) -> None:
        print("Batches:")
        for batch in batch_repo.get_all():
            print(
                f"ID: {batch.getId()}, Name: {batch.getName()},"
                f" Price : {batch.getPrice()}"
            )
        print("-" * 50)

    @staticmethod
    def print_discounts(discount_repo: DiscountRepository) -> None:
        print("Discounts:")
        for discount in discount_repo.get_all():
            if isinstance(discount, PercentageDiscount):
                print(
                    f"ID: {discount.getId()}, Item ID: {discount.getItemId()},"
                    f" Percentage: {discount.getValue()}"
                )
        print("-" * 50)


if __name__ == "__main__":
    # Create items
    milk = Item(id=1, name="Milk", price=4.99)
    water = Item(id=2, name="Mineral Water", price=3.00)

    # Apply a discount strategy to an item (optional)
    discount_strategy = PercentageDiscountStrategy(percentage=0.1)
    milk.setDiscountStrategy(discount_strategy)

    # Create a batch of mineral water
    water_batch = Batch(id=3, amount=4, item_type=water)

    # Create a receipt and add items to it
    receipt = Receipt(id=123, sellables=[milk, water_batch, water])

    # Print the receipt using the Printer class
    Printer.print_receipt(receipt)
