import sqlite3
from dataclasses import dataclass
from typing import List

import pytest

from database import (
    BatchRepository,
    DiscountRepository,
    DoesNotExistError,
    ExistsError,
    ItemRepository,
)
from entities import Batch, Discount, Item, PercentageDiscount, Sellable


# Es yovelive rac sqllite-s ukavshirdeba sakmaod glexurad weria
# magram didi bodishi agar shemidzlia davigale
@dataclass
class SQLiteDBCreator:
    db_name: str = "pos.db"

    def create_tables(self) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Create the 'items' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY UNIQUE,
                    name TEXT NOT NULL,
                    price REAL NOT NULL
                )
            """
            )

            # Create the 'discounts' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS discounts (
                    discount_id INTEGER PRIMARY KEY UNIQUE,
                    item_id INTEGER NOT NULL,
                    value REAL NOT NULL,
                    FOREIGN KEY (item_id) REFERENCES items (item_id)
                )
            """
            )

            # Create the 'batch_items' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS batch_items (
                    batch_id INTEGER NOT NULL,
                    item_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    PRIMARY KEY (batch_id, item_id),
                    FOREIGN KEY (item_id) REFERENCES items (item_id)
                )
            """
            )

    def drop_tables(self) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS items")
            cursor.execute("DROP TABLE IF EXISTS discounts")
            cursor.execute("DROP TABLE IF EXISTS batch_items")


class SQLiteItemRepository(ItemRepository):
    db_name: str = "pos.db"

    def create(self, sellable: Item) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO items (item_id, name, price) VALUES (?, ?, ?)",
                    (sellable.getId(), sellable.getName(), sellable.getPrice()),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ExistsError

    def read(self, sellable_id: int) -> Item:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items WHERE item_id = ?", (sellable_id,))
            row = cursor.fetchone()
            if row:
                return Item(id=row[0], name=row[1], price=row[2])
            else:
                raise DoesNotExistError

    def update(self, sellable: Item) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE items SET name=?, price=? WHERE item_id=?",
                (sellable.getName(), sellable.getPrice(), sellable.getId()),
            )
            conn.commit()

    def delete(self, sellable_id: int) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items WHERE item_id=?", (sellable_id,))
            conn.commit()

    def get_all(self) -> List[Sellable]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM items")
            rows = cursor.fetchall()
            return [Item(id=row[0], name=row[1], price=row[2]) for row in rows]


class SQLiteDiscountRepository(DiscountRepository):
    db_name: str = "pos.db"

    def create(self, discount: Discount) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO discounts (discount_id, item_id, value)"
                    " VALUES (?, ?, ?)",
                    (discount.getId(), discount.getItemId(), discount.getValue()),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ExistsError

    def read(self, discount_id: int) -> Discount:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM discounts WHERE discount_id = ?", (discount_id,)
            )
            row = cursor.fetchone()
            if row:
                return PercentageDiscount(id=row[0], item_id=row[1], percentage=row[2])
            else:
                raise DoesNotExistError

    def update(self, discount: Discount) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE discounts SET item_id=?, value=? WHERE discount_id=?",
                (discount.getItemId(), discount.getValue(), discount.getId()),
            )
            conn.commit()

    def delete(self, discount_id: int) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM discounts WHERE discount_id=?", (discount_id,))
            conn.commit()

    def get_item_discount(self, item_id: int) -> float:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM discounts WHERE item_id=?", (item_id,))
            row = cursor.fetchone()
            if row and row[0] >= 0:
                return float(row[0])
            else:
                return 0.0

    def get_all(self) -> List[Discount]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM discounts")
            rows = cursor.fetchall()
            return [
                PercentageDiscount(id=row[0], item_id=row[1], percentage=row[2])
                for row in rows
            ]


@dataclass
class SQLiteBatchRepository(BatchRepository):
    db_name: str = "pos.db"

    def create(self, batch: Batch) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO batch_items (batch_id, item_id, amount)"
                    " VALUES (?, ?, ?)",
                    (batch.getId(), batch.getItem().getId(), batch.getAmount()),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                raise ExistsError

    def read(self, batch_id: int) -> Batch:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT bi.batch_id, bi.amount, i.item_id, i.name, i.price
                FROM batch_items bi
                JOIN items i ON bi.item_id = i.item_id
                WHERE bi.batch_id = ?
                """,
                (batch_id,),
            )
            result = cursor.fetchall()

            if not result:
                raise DoesNotExistError

            batch_data = result[0]
            item_data = batch_data[2:5]
            item = Item(*item_data)
            batch = Batch(batch_data[0], batch_data[1], item)

            return batch

    def update(self, batch: Batch) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE batch_items SET amount = ? WHERE batch_id = ? AND item_id = ?",
                (batch.getAmount(), batch.getId(), batch.getItem().getId()),
            )
            if cursor.rowcount == 0:
                raise DoesNotExistError
            conn.commit()

    def delete(self, batch_id: int) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM batch_items WHERE batch_id = ?", (batch_id,))
            if cursor.rowcount == 0:
                raise DoesNotExistError
            conn.commit()

    def get_all(self) -> List[Sellable]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT bi.batch_id, bi.amount, i.item_id, i.name, i.price
                FROM batch_items bi
                JOIN items i ON bi.item_id = i.item_id
                """
            )
            result = cursor.fetchall()

            batches: List[Sellable] = []
            for batch_data in result:
                item_data = batch_data[2:5]
                item = Item(*item_data)
                batch = Batch(batch_data[0], batch_data[1], item)
                batches.append(batch)

            return batches


def test_sqlite_item_repository() -> None:
    db_creator = SQLiteDBCreator()
    db_creator.drop_tables()
    db_creator.create_tables()
    # Arrange
    item_repository = SQLiteItemRepository()

    # Create a test item
    test_item = Item(id=1, name="Test Item", price=10.0)

    # Act
    # Test create
    item_repository.create(test_item)
    with pytest.raises(ExistsError):
        item_repository.create(test_item)

    # Test read
    retrieved_item = item_repository.read(1)
    assert retrieved_item == test_item

    # Test update
    updated_item = Item(id=1, name="Updated Test Item", price=15.0)
    item_repository.update(updated_item)
    updated_item_after_update = item_repository.read(1)
    assert updated_item_after_update == updated_item

    # Test delete
    item_repository.delete(1)
    with pytest.raises(DoesNotExistError):
        item_repository.read(1)

    # Test get_all
    test_items = [
        Item(id=2, name="Item 2", price=20.0),
        Item(id=3, name="Item 3", price=25.0),
    ]
    for item in test_items:
        item_repository.create(item)

    all_items = item_repository.get_all()
    assert all_items == test_items

    # Test does not exist error
    with pytest.raises(DoesNotExistError):
        item_repository.read(100)


def test_sqlite_discount_repository() -> None:
    db_creator = SQLiteDBCreator()
    db_creator.drop_tables()
    db_creator.create_tables()
    # Arrange
    item_repository = SQLiteItemRepository()
    # Create a test item
    test_item = Item(id=1, name="Test Item", price=10.0)
    item_repository.create(test_item)
    # Arrange
    discount_repository = SQLiteDiscountRepository()

    # Create a test discount
    test_discount = PercentageDiscount(id=1, item_id=1, percentage=0.1)

    # Act
    # Test create
    discount_repository.create(test_discount)

    # Test existence error
    with pytest.raises(ExistsError):
        discount_repository.create(test_discount)

    # Test read
    retrieved_discount = discount_repository.read(1)
    assert retrieved_discount == test_discount

    # Test update
    updated_discount = PercentageDiscount(id=1, item_id=2, percentage=0.15)
    discount_repository.update(updated_discount)
    updated_discount_after_update = discount_repository.read(1)
    assert updated_discount_after_update == updated_discount

    # Test delete
    discount_repository.delete(1)
    with pytest.raises(DoesNotExistError):
        discount_repository.read(1)

    # Test get_item_discount
    test_item_id = 2
    test_discount_value = 0.2
    discount_repository.create(
        PercentageDiscount(id=2, item_id=test_item_id, percentage=test_discount_value)
    )
    retrieved_item_discount = discount_repository.get_item_discount(test_item_id)
    assert retrieved_item_discount == test_discount_value

    # Test does not exist error
    with pytest.raises(DoesNotExistError):
        discount_repository.read(100)


def test_sqlite_batch_repository() -> None:
    db_creator = SQLiteDBCreator()
    db_creator.drop_tables()
    db_creator.create_tables()

    # Arrange
    batch_repository = SQLiteBatchRepository()
    item_repository = SQLiteItemRepository()

    # Create a test item
    test_item = Item(id=1, name="Test Item", price=10.0)
    item_repository.create(test_item)
    batch_item = Batch(id=1, amount=5, item_type=test_item)

    # Act
    # Test create
    batch_repository.create(batch_item)
    with pytest.raises(ExistsError):
        batch_repository.create(batch_item)

    # Test read
    retrieved_batch = batch_repository.read(1)
    assert retrieved_batch == batch_item

    # Test update
    updated_batch = Batch(id=1, amount=10, item_type=test_item)
    batch_repository.update(updated_batch)
    updated_batch_after_update = batch_repository.read(1)
    assert updated_batch_after_update == updated_batch

    # Test delete
    batch_repository.delete(1)
    with pytest.raises(DoesNotExistError):
        batch_repository.read(1)

    # Test get_all
    test_batches = [
        Batch(id=2, amount=8, item_type=test_item),
        Batch(id=3, amount=15, item_type=test_item),
    ]
    for batch in test_batches:
        batch_repository.create(batch)

    all_batches = batch_repository.get_all()
    assert all_batches == test_batches

    # Test does not exist error
    with pytest.raises(DoesNotExistError):
        batch_repository.read(100)
