import sqlite3
from dataclasses import dataclass
from uuid import UUID

from core.products import Product, ProductDoesNotExistError, ProductExistsError


@dataclass
class SQLiteProducts:
    db_name: str

    def create(self, product: Product) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO products (id, unit_id,"
                    " name, barcode, price) VALUES (?, ?, ?, ?, ?)",
                    (
                        str(product.id),
                        str(product.unit_id),
                        product.name,
                        product.barcode,
                        product.price,
                    ),
                )
            except sqlite3.IntegrityError:
                raise ProductExistsError(
                    f"Product with barcode '{product.barcode}' already exists"
                )

    def read(self, product_id: UUID) -> Product:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, unit_id, name, barcode, price FROM products WHERE id = ?",
                (str(product_id),),
            )
            result = cursor.fetchone()

            if result is None:
                raise ProductDoesNotExistError(
                    f"Product with id '{product_id}' does not exist"
                )

            return Product(
                id=UUID(result[0]),
                unit_id=UUID(result[1]),
                name=result[2],
                barcode=result[3],
                price=result[4],
            )

    def update(self, product: Product) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE products SET unit_id = ?, name = ?,"
                " barcode = ?, price = ? WHERE id = ?",
                (
                    str(product.unit_id),
                    product.name,
                    product.barcode,
                    product.price,
                    str(product.id),
                ),
            )

            if cursor.rowcount == 0:
                raise ProductDoesNotExistError(
                    f"Product with id '{product.id}' does not exist"
                )

    def delete(self, product_id: UUID) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (str(product_id),))

            if cursor.rowcount == 0:
                raise ProductDoesNotExistError(
                    f"Product with id '{product_id}' does not exist"
                )

    def read_all(self) -> list[Product]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, unit_id, name, barcode, price FROM products")
            results = cursor.fetchall()

            return [
                Product(
                    id=UUID(result[0]),
                    unit_id=UUID(result[1]),
                    name=result[2],
                    barcode=result[3],
                    price=result[4],
                )
                for result in results
            ]
