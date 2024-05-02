from uuid import UUID, uuid4

import pytest

from core.products import Product, ProductDoesNotExistError, ProductExistsError
from infra.repos.in_memory.in_memory_products import InMemoryProducts
from tests.fake_generator import FakeGenerator


@pytest.fixture
def fake_generator() -> FakeGenerator:
    return FakeGenerator()


def test_should_create_product(fake_generator: FakeGenerator) -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    fake_product: Product = fake_generator.generate_product()

    product_repository.create(fake_product)
    assert product_repository.read(fake_product.id) == fake_product


def test_should_not_create_duplicate_product(fake_generator: FakeGenerator) -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    fake_product1: Product = fake_generator.generate_product()
    fake_product2: Product = fake_generator.generate_product()
    fake_product2.id = fake_product1.id

    product_repository.create(fake_product1)

    with pytest.raises(ProductExistsError):
        product_repository.create(fake_product2)


def test_should_read_product(fake_generator: FakeGenerator) -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    fake_product: Product = fake_generator.generate_product()

    product_repository.create(fake_product)
    retrieved_product: Product = product_repository.read(fake_product.id)
    assert retrieved_product == fake_product


def test_should_not_read_nonexistent_product() -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    unknown_product_id: UUID = uuid4()

    with pytest.raises(ProductDoesNotExistError):
        product_repository.read(unknown_product_id)


def test_should_update_product(fake_generator: FakeGenerator) -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    fake_product: Product = fake_generator.generate_product()

    product_repository.create(fake_product)

    new_price: float = 25.0
    fake_product.set_price(new_price)
    product_repository.update(fake_product)

    updated_product: Product = product_repository.read(fake_product.id)
    assert updated_product.get_price() == new_price


def test_should_not_update_nonexistent_product() -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    unknown_product_id: UUID = uuid4()

    with pytest.raises(ProductDoesNotExistError):
        fake_product: Product = Product(
            name="TestProduct",
            barcode="1234567890123",
            price=15.0,
            id=unknown_product_id,
            unit_id=uuid4(),
        )
        product_repository.update(fake_product)


def test_should_delete_product(fake_generator: FakeGenerator) -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    fake_product: Product = fake_generator.generate_product()

    product_repository.create(fake_product)
    product_repository.delete(fake_product.id)

    with pytest.raises(ProductDoesNotExistError):
        product_repository.read(fake_product.id)


def test_should_not_delete_nonexistent_product() -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    unknown_product_id: UUID = uuid4()

    with pytest.raises(ProductDoesNotExistError):
        product_repository.delete(unknown_product_id)


def test_should_read_all_products(fake_generator: FakeGenerator) -> None:
    product_repository: InMemoryProducts = InMemoryProducts()
    fake_product1: Product = fake_generator.generate_product()
    fake_product2: Product = fake_generator.generate_product()

    product_repository.create(fake_product1)
    product_repository.create(fake_product2)

    all_products: list[Product] = product_repository.read_all()
    assert fake_product1 in all_products
    assert fake_product2 in all_products
