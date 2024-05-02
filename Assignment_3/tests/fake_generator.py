from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from faker import Faker

from core.products import Product
from core.units import Unit


@dataclass
class FakeGenerator:
    faker: Faker = field(default_factory=Faker)

    def generate_unit_item(self, name: str = "") -> dict[str, Any]:
        return {"name": name or self.faker.word()}

    def generate_product_item(self, unit_id: UUID = uuid4()) -> dict[str, Any]:
        return {
            "unit_id": str(unit_id) or str(uuid4()),
            "name": self.faker.word(),
            "barcode": self.faker.ean13(),
            "price": round(self.faker.random.uniform(1, 50), 2),
        }

    def generate_receipt_product_item(
        self, product_id: UUID = uuid4(), quantity: int = 1
    ) -> dict[str, Any]:
        return {
            "id": str(product_id) or str(uuid4()),
            "quantity": quantity,
            "price": round(self.faker.random.uniform(1, 50), 2),
        }

    def generate_unit(self, name: str = "") -> Unit:
        return Unit(name=name or self.faker.word())

    def generate_product(self, unit_id: UUID = uuid4()) -> Product:
        return Product(
            name=self.faker.word(),
            barcode=self.faker.ean13(),
            price=round(self.faker.random.uniform(1, 50), 2),
            id=uuid4(),
            unit_id=unit_id,
        )
