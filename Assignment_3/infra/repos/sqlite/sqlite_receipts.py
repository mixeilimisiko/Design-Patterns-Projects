import sqlite3
from dataclasses import dataclass
from uuid import UUID

from core.products import Product
from core.receipts import (
    Receipt,
    ReceiptClosedError,
    ReceiptDoesNotExistError,
    ReceiptExistsError,
    ReceiptProduct,
)


@dataclass
class SQLiteReceipts:
    db_name: str = "pos.db"

    def create(self, receipt: Receipt) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO receipts (id, status) VALUES (?, ?)",
                    (str(receipt.id), receipt.status),
                )
            except sqlite3.IntegrityError:
                raise ReceiptExistsError(
                    f"Receipt with id '{receipt.id}' already exists"
                )

    def add_product(self, receipt_id: UUID, product: ReceiptProduct) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Check if receipt exists and is not closed
            cursor.execute(
                "SELECT status FROM receipts WHERE id = ?", (str(receipt_id),)
            )
            result = cursor.fetchone()

            if result is None:
                raise ReceiptDoesNotExistError(
                    f"Receipt with id '{receipt_id}' does not exist"
                )

            receipt_status = result[0]

            if receipt_status == "closed":
                raise ReceiptClosedError(f"Receipt with id '{receipt_id}' is closed")

            # Check if product already exists in the receipt
            cursor.execute(
                "SELECT quantity FROM receipt_products"
                " WHERE receipt_id = ? AND product_id = ?",
                (str(receipt_id), str(product.inner.id)),
            )
            existing_quantity_result = cursor.fetchone()

            if existing_quantity_result is not None:
                existing_quantity = existing_quantity_result[0]
                new_quantity = existing_quantity + product.quantity
                # Update the quantity of the existing product
                cursor.execute(
                    "UPDATE receipt_products SET quantity = ?"
                    " WHERE receipt_id = ? AND product_id = ?",
                    (new_quantity, str(receipt_id), str(product.inner.id)),
                )
            else:
                # Insert the new product
                cursor.execute(
                    "INSERT INTO receipt_products (receipt_id, product_id, quantity)"
                    " VALUES (?, ?, ?)",
                    (str(receipt_id), str(product.inner.id), product.quantity),
                )

    def read(self, receipt_id: UUID) -> Receipt:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, status FROM receipts" " WHERE id = ?", (str(receipt_id),)
            )
            result = cursor.fetchone()

            if result is None:
                raise ReceiptDoesNotExistError(
                    f"Receipt with id '{receipt_id}' does not exist"
                )

            receipt = Receipt(id=UUID(result[0]), status=result[1])
            cursor.execute(
                "SELECT product_id, quantity FROM receipt_products"
                " WHERE receipt_id = ?",
                (str(receipt_id),),
            )
            product_results = cursor.fetchall()

            for product_result in product_results:
                product_id, quantity = product_result

                # Fetch product details from the 'products' table
                cursor.execute(
                    "SELECT unit_id, name, barcode, price FROM products"
                    " WHERE id = ?",
                    (str(product_id),),
                )
                product_details = cursor.fetchone()

                if product_details is not None:
                    unit_id, name, barcode, price = product_details
                    product = Product(
                        id=UUID(product_id),
                        unit_id=UUID(unit_id),
                        name=name,
                        barcode=barcode,
                        price=price,
                    )
                    receipt_product = ReceiptProduct(inner=product, quantity=quantity)
                    receipt.add_product(receipt_product)

            return receipt

    def update_status(self, receipt_id: UUID, receipt_status: str) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE receipts SET status = ? WHERE id = ?",
                (receipt_status, str(receipt_id)),
            )

            if cursor.rowcount == 0:
                raise ReceiptDoesNotExistError(
                    f"Receipt with id '{receipt_id}' does not exist"
                )

    def delete(self, receipt_id: UUID) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Check if receipt exists and is not closed
            cursor.execute(
                "SELECT status FROM receipts WHERE id = ?", (str(receipt_id),)
            )
            result = cursor.fetchone()

            if result is None:
                raise ReceiptDoesNotExistError(
                    f"Receipt with id '{receipt_id}' does not exist"
                )

            receipt_status = result[0]

            if receipt_status == "closed":
                raise ReceiptClosedError(f"Receipt with id '{receipt_id}' is closed")

            cursor.execute("DELETE FROM receipts" " WHERE id = ?", (str(receipt_id),))

            if cursor.rowcount == 0:
                raise ReceiptDoesNotExistError(
                    f"Receipt with id '{receipt_id}' does not exist"
                )

    def read_all(self) -> list[Receipt]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Fetch all receipts
            cursor.execute("SELECT id, status FROM receipts")
            receipt_results = cursor.fetchall()

            receipts = []

            for receipt_result in receipt_results:
                receipt_id, receipt_status = receipt_result
                receipt = Receipt(id=UUID(receipt_id), status=receipt_status)

                # Fetch products for each receipt
                cursor.execute(
                    "SELECT product_id, quantity FROM receipt_products"
                    " WHERE receipt_id = ?",
                    (str(receipt_id),),
                )
                product_results = cursor.fetchall()

                for product_result in product_results:
                    product_id, quantity = product_result

                    # Fetch product details from the 'products' table
                    cursor.execute(
                        "SELECT unit_id, name, barcode, price FROM products"
                        " WHERE id = ?",
                        (str(product_id),),
                    )
                    product_details = cursor.fetchone()

                    if product_details is not None:
                        unit_id, name, barcode, price = product_details
                        product = Product(
                            id=UUID(product_id),
                            unit_id=UUID(unit_id),
                            name=name,
                            barcode=barcode,
                            price=price,
                        )
                        receipt_product = ReceiptProduct(
                            inner=product, quantity=quantity
                        )
                        receipt.add_product(receipt_product)

                receipts.append(receipt)

            return receipts
