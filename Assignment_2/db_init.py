from typing import Dict, List

from database import (
    BatchRepository,
    DiscountRepository,
    InMemoryBatchRepository,
    InMemoryDiscountRepository,
    InMemoryItemRepository,
    ItemRepository,
)
from entities import Batch, Item, PercentageDiscount
from real_database import (
    SQLiteBatchRepository,
    SQLiteDiscountRepository,
    SQLiteItemRepository,
)


class ItemInitializer:
    @staticmethod
    def initialize_item_repository(inmemory: bool = False) -> ItemRepository:
        item_repo: ItemRepository = InMemoryItemRepository()
        if not inmemory:
            item_repo = SQLiteItemRepository()

        products_data: List[Dict[str, str]] = [
            {"id": "1", "name": "Bread", "price": "2.49"},
            {"id": "2", "name": "Beer ", "price": "2.99"},
            {"id": "3", "name": "Milk", "price": "1.99"},
            {"id": "4", "name": "Mineral Water", "price": "0.99"},
            {"id": "5", "name": "Chips", "price": "3.49"},
            {"id": "6", "name": "Yogurt", "price": "2.29"},
            {"id": "7", "name": "Spaghetti", "price": "1.29"},
            {"id": "8", "name": "Orange Juice", "price": "4.49"},
            # more products as needed
        ]

        for data in products_data:
            id: int = int(data["id"])
            name: str = data["name"]
            price: float = float(data["price"])
            product = Item(id=id, name=name, price=price)
            item_repo.create(product)

        # for p in item_repo.get_all():
        #     print("product id " + str(p.getId()) + " " + p.getName())

        return item_repo


class DiscountInitializer:
    @staticmethod
    def initialize_discount_repository(inmemory: bool = False) -> DiscountRepository:
        discount_repo: DiscountRepository = InMemoryDiscountRepository()
        if not inmemory:
            discount_repo = SQLiteDiscountRepository()

        # Add percentage discounts for specific items
        discounts_data = [
            {"id": 1, "item_id": 1, "percentage": 0.1},  # 10% discount on Bread
            {"id": 2, "item_id": 2, "percentage": 0.05},  # 5% discount on Beer (6-pack)
            {
                "id": 3,
                "item_id": 4,
                "percentage": 0.15,
            },  # 15% discount on Mineral Water
            # more discounts as needed
        ]

        for data in discounts_data:
            discount = PercentageDiscount(
                id=int(data["id"]),
                item_id=int(data["item_id"]),
                percentage=float(data["percentage"]),
            )
            discount_repo.create(discount)

        # for d in discount_repo.get_all():
        #     print("product id " + str(d.getId()) + " " + str(d.getValue()))

        return discount_repo


class BatchRepositoryInitializer:
    @staticmethod
    def initialize_batch_repository(
        item_repo: ItemRepository, inmemory: bool = False
    ) -> BatchRepository:
        batch_repo: BatchRepository = InMemoryBatchRepository()
        if not inmemory:
            batch_repo = SQLiteBatchRepository()

        # Add batches for specific items
        batches_data = [
            {"id": 1, "amount": 3, "item_id": 1},  # 3-pack of Bread
            {"id": 2, "amount": 2, "item_id": 2},  # 2-pack of Beer (6-pack)
            {"id": 3, "amount": 5, "item_id": 4},  # 5-pack of Mineral Water
            # Add more batches as needed
        ]

        for data in batches_data:
            item = item_repo.read(data["item_id"])
            batch = Batch(id=int(data["id"]), amount=data["amount"], item_type=item)
            batch_repo.create(batch)

        return batch_repo
