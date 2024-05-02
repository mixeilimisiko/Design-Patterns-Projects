from typing import Any
from unittest.mock import ANY
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from httpx import Response

from tests.fake_generator import FakeGenerator


@pytest.fixture
def client() -> TestClient:
    from runner.setup import init_app

    return TestClient(init_app())


@pytest.fixture
def datoou_unit(client: TestClient, fake_generator: FakeGenerator) -> dict[str, Any]:
    unit_data = fake_generator.generate_unit_item(name="datoou")

    create_response = client.post("/units", json=unit_data)
    assert create_response.status_code == 201
    ret: dict[str, dict[str, Any]] = create_response.json()["unit"]
    return ret


@pytest.fixture
def fake_generator() -> FakeGenerator:
    return FakeGenerator(Faker())


def assert_error(response: Response, status_code: int, message: str) -> None:
    assert response.status_code == status_code
    assert "detail" in response.json()
    assert "error" in response.json()["detail"]
    assert message in response.json()["detail"]["error"]["message"]


def test_should_not_create_product_with_unknown_unit_id(
    client: TestClient, fake_generator: FakeGenerator
) -> None:
    product_data = fake_generator.generate_product_item()

    response = client.post("/products", json=product_data)

    unit_id = product_data["unit_id"]
    assert_error(response, 404, f"Unit with id {unit_id} does not exist.")


def test_should_create_product(
    client: TestClient, datoou_unit: dict[str, Any], fake_generator: FakeGenerator
) -> None:
    product_data = fake_generator.generate_product_item(unit_id=datoou_unit["id"])

    response = client.post("/products", json=product_data)

    assert response.status_code == 201
    assert "product" in response.json()

    created_product = response.json()["product"]
    assert "id" in created_product
    assert created_product == {"id": ANY, **product_data}


def test_should_not_read_unknown_product(
    client: TestClient, fake_generator: FakeGenerator
) -> None:
    unknown_product_id = uuid4()

    response = client.get(f"/products/{unknown_product_id}")

    assert_error(response, 404, f"Product with id {unknown_product_id} does not exist.")


def test_should_persist_product(
    client: TestClient, datoou_unit: dict[str, Any], fake_generator: FakeGenerator
) -> None:
    product_data = fake_generator.generate_product_item(unit_id=datoou_unit["id"])

    create_product_response = client.post("/products", json=product_data)
    assert create_product_response.status_code == 201
    created_product = create_product_response.json()["product"]

    product_id = created_product["id"]
    read_product_response = client.get(f"/products/{product_id}")
    assert read_product_response.status_code == 200
    retrieved_product = read_product_response.json()["product"]

    assert retrieved_product == created_product


def test_should_not_duplicate_product(
    client: TestClient, datoou_unit: dict[str, Any], fake_generator: FakeGenerator
) -> None:
    product_data = fake_generator.generate_product_item(unit_id=datoou_unit["id"])

    create_product_response = client.post("/products", json=product_data)
    assert create_product_response.status_code == 201
    created_product = create_product_response.json()["product"]

    create_duplicate_response = client.post("/products", json=product_data)

    barcode = created_product["barcode"]
    assert_error(
        create_duplicate_response,
        409,
        f"Product with barcode '{barcode}' already exists",
    )


def test_get_all_products_on_empty(
    client: TestClient, fake_generator: FakeGenerator
) -> None:
    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": []}


def test_get_all_products(
    client: TestClient, datoou_unit: dict[str, Any], fake_generator: FakeGenerator
) -> None:
    unit_id = datoou_unit["id"]

    product_data = fake_generator.generate_product_item(unit_id)

    response_product = client.post("/products", json=product_data)
    product_id = response_product.json()["product"]["id"]

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == {"products": [{"id": product_id, **product_data}]}


def test_should_update_product(
    client: TestClient, datoou_unit: dict[str, Any], fake_generator: FakeGenerator
) -> None:
    product_data = fake_generator.generate_product_item(unit_id=datoou_unit["id"])

    create_product_response = client.post("/products", json=product_data)
    assert create_product_response.status_code == 201
    created_product = create_product_response.json()["product"]

    new_price = 19.99
    update_response = client.patch(
        f"/products/{created_product['id']}", json={"price": new_price}
    )
    assert update_response.status_code == 200
    assert update_response.json() == {"message": "Product updated successfully"}

    read_product_response = client.get(f"/products/{created_product['id']}")
    assert read_product_response.status_code == 200
    updated_product = read_product_response.json()["product"]

    assert updated_product["price"] == new_price


def test_should_not_update_unknown_product(
    client: TestClient, datoou_unit: dict[str, Any], fake_generator: FakeGenerator
) -> None:
    new_price = 29.85
    unknown_product_id = uuid4()
    update_response = client.patch(
        f"/products/{unknown_product_id}", json={"price": new_price}
    )
    assert_error(
        update_response, 404, f"Product with id {unknown_product_id} does not exist."
    )
