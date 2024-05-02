from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4

from core.units import UnitDoesNotExistError, UnitRepository


@dataclass
class Product:
    name: str
    barcode: str
    price: float
    id: UUID = field(default_factory=uuid4)
    unit_id: UUID = field(default_factory=uuid4)

    def get_price(self) -> float:
        return self.price

    def set_price(self, price: float) -> None:
        self.price = price

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name


class ProductRepository(Protocol):
    def create(self, product: Product) -> None:
        pass

    def read(self, product_id: UUID) -> Product:
        pass

    def update(self, product: Product) -> None:
        pass

    def delete(self, product_id: UUID) -> None:
        pass

    def read_all(self) -> list[Product]:
        pass


class ProductExistsError(Exception):
    pass


class ProductDoesNotExistError(Exception):
    pass


@dataclass
class ProductService:
    products: ProductRepository
    units: UnitRepository
    pass

    def create_product(
        self, unit_id: UUID, name: str, barcode: str, price: float
    ) -> Product:
        # Validate if the unit_id exists in the Unit Repository
        try:
            self.units.read(unit_id)
        except UnitDoesNotExistError as e:
            raise e
        new_product = Product(
            unit_id=unit_id, name=name, barcode=barcode, price=price, id=uuid4()
        )
        try:
            self.products.create(new_product)
            return new_product
        except ProductExistsError as e:
            raise e

    def fetch(self, product_id: UUID) -> Product:
        try:
            return self.products.read(product_id)
        except ProductDoesNotExistError as e:
            raise e

    def update_product(self, product_id: UUID, price: float) -> None:
        try:
            product = self.products.read(product_id)
            product.set_price(price)
            self.products.update(product)
        except ProductDoesNotExistError as e:
            raise e

    def fetch_all_products(self) -> list[Product]:
        return self.products.read_all()
