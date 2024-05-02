import sqlite3
from dataclasses import dataclass

from infra.repos.sqlite.sqlite_products import SQLiteProducts
from infra.repos.sqlite.sqlite_receipts import SQLiteReceipts
from infra.repos.sqlite.sqlite_units import SQLiteUnits


@dataclass
class DbManager:
    db_name: str = "pos.db"

    def create_tables(self) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Create the 'units' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS units (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE
                )
                """
            )

            # Create the 'products' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    unit_id TEXT,
                    name TEXT,
                    barcode TEXT UNIQUE,
                    price REAL,
                    FOREIGN KEY (unit_id) REFERENCES units (id)
                )
                """
            )

            # Create the 'receipts' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY,
                    status TEXT
                )
                """
            )

            # Create the 'receipt_products' table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS receipt_products (
                    receipt_id TEXT,
                    product_id TEXT,
                    quantity INTEGER,
                    PRIMARY KEY (receipt_id, product_id),
                    FOREIGN KEY (receipt_id) REFERENCES receipts (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
                """
            )

    def drop_tables(self) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DROP TABLE IF EXISTS units")
            cursor.execute("DROP TABLE IF EXISTS products")
            cursor.execute("DROP TABLE IF EXISTS receipts")
            cursor.execute("DROP TABLE IF EXISTS receipt_products")

    def get_unit_repository(self) -> SQLiteUnits:
        return SQLiteUnits(self.db_name)

    def get_product_repository(self) -> SQLiteProducts:
        return SQLiteProducts(self.db_name)

    def get_receipt_repository(self) -> SQLiteReceipts:
        return SQLiteReceipts(self.db_name)
