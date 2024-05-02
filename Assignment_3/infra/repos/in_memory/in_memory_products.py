from dataclasses import dataclass, field
from uuid import UUID

from core.products import Product, ProductDoesNotExistError, ProductExistsError


@dataclass
class InMemoryProducts:
    products: dict[UUID, Product] = field(default_factory=dict)

    def create(self, product: Product) -> None:
        if product.id in self.products:
            raise ProductExistsError(f"Product with id '{product.id}' already exists")
        for existing_product in self.products.values():
            if existing_product.barcode == product.barcode:
                raise ProductExistsError(
                    f"Product with barcode '{product.barcode}' already exists"
                )

        self.products[product.id] = product

    def read(self, product_id: UUID) -> Product:
        try:
            return self.products[product_id]
        except KeyError:
            raise ProductDoesNotExistError(
                f"Product with id '{product_id}' does not exist"
            )

    def update(self, product: Product) -> None:
        if product.id not in self.products:
            raise ProductDoesNotExistError(
                f"Product with id '{product.id}' does not exist"
            )

        self.products[product.id] = product

    def delete(self, product_id: UUID) -> None:
        if product_id not in self.products:
            raise ProductDoesNotExistError(
                f"Product with id '{product_id}' does not exist"
            )

        del self.products[product_id]

    def read_all(self) -> list[Product]:
        return list(self.products.values())
