from typing import Any
from unittest.mock import ANY
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient
from httpx import Response

from runner.setup import init_app
from tests.fake_generator import FakeGenerator


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


@pytest.fixture
def fake_generator(client: TestClient) -> FakeGenerator:
    return FakeGenerator(Faker())


@pytest.fixture
def default_product(
    client: TestClient, fake_generator: FakeGenerator
) -> dict[str, Any]:
    unit_data = fake_generator.generate_unit_item(name="kg")

    create_unit_response = client.post("/units", json=unit_data)
    assert create_unit_response.status_code == 201
    kg_unit = create_unit_response.json()["unit"]

    product_data = fake_generator.generate_product_item(unit_id=kg_unit["id"])

    create_product_response = client.post("/products", json=product_data)
    assert create_product_response.status_code == 201
    ret: dict[str, Any] = create_product_response.json()["product"]
    return ret


def product_to_receipt_product(
    product: dict[str, Any], quantity: int
) -> dict[str, Any]:
    """
    Convert a regular product to a receipt product with the specified quantity.
    """
    return {
        "id": product["id"],
        "quantity": quantity,
        "price": product["price"],
        "total": quantity * product["price"],
    }


def assert_error(response: Response, status_code: int, message: str) -> None:
    assert response.status_code == status_code
    assert "detail" in response.json()
    assert "error" in response.json()["detail"]
    assert message in response.json()["detail"]["error"]["message"]


def test_should_not_read_unknown(client: TestClient) -> None:
    unknown_receipt_id = uuid4()

    response = client.get(f"/receipts/{unknown_receipt_id}")

    assert_error(response, 404, f"Receipt with id {unknown_receipt_id} does not exist.")


def test_should_create(client: TestClient, default_product: dict[str, Any]) -> None:
    response = client.post("/receipts")

    assert response.status_code == 201
    assert "receipt" in response.json()

    created_receipt = response.json()["receipt"]
    assert "id" in created_receipt
    assert created_receipt == {"id": ANY, "status": "open", "products": [], "total": 0}


def test_should_persist(client: TestClient) -> None:
    create_receipt_response = client.post("/receipts")

    assert create_receipt_response.status_code == 201

    receipt_id = create_receipt_response.json()["receipt"]["id"]

    read_receipt_response = client.get(f"/receipts/{receipt_id}")

    assert read_receipt_response.status_code == 200
    retrieved_receipt = read_receipt_response.json()["receipt"]

    assert retrieved_receipt["id"] == receipt_id


def test_should_add_product(
    client: TestClient, default_product: dict[str, Any]
) -> None:
    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    quantity = 3
    add_product_response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": default_product["id"], "quantity": quantity},
    )

    assert add_product_response.status_code == 201
    assert "receipt" in add_product_response.json()

    updated_receipt = add_product_response.json()["receipt"]
    assert "id" in updated_receipt
    assert updated_receipt == {
        "id": receipt_id,
        "status": "open",
        "products": ANY,
        "total": ANY,
    }

    read_response = client.get(f"/receipts/{receipt_id}")

    assert read_response.status_code == 200
    retrieved_receipt = read_response.json()["receipt"]

    assert (
        product_to_receipt_product(default_product, quantity)
        in retrieved_receipt["products"]
    )


def test_should_sum_quantity_when_adding_same_product(
    client: TestClient, default_product: dict[str, Any]
) -> None:
    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    quantity = 5
    add_product_response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": default_product["id"], "quantity": quantity},
    )

    assert add_product_response.status_code == 201
    assert "receipt" in add_product_response.json()

    add_product_response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": default_product["id"], "quantity": quantity},
    )

    updated_receipt = add_product_response.json()["receipt"]
    assert "id" in updated_receipt
    assert updated_receipt == {
        "id": receipt_id,
        "status": "open",
        "products": ANY,
        "total": ANY,
    }

    read_response = client.get(f"/receipts/{receipt_id}")

    assert read_response.status_code == 200
    retrieved_receipt = read_response.json()["receipt"]

    assert (
        product_to_receipt_product(default_product, 2 * quantity)
        in retrieved_receipt["products"]
    )


def test_should_not_add_unknown_product(client: TestClient) -> None:
    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    quantity = 3
    unknown_product_id = str(uuid4())
    add_product_response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": unknown_product_id, "quantity": quantity},
    )

    assert_error(
        add_product_response,
        404,
        f"Product with id {unknown_product_id} does not exist.",
    )


def test_should_not_add_to_unknown_receipt(client: TestClient) -> None:
    quantity = 3
    unknown_receipt_id = str(uuid4())
    add_product_response = client.post(
        f"/receipts/{unknown_receipt_id}/products",
        json={"id": str(uuid4()), "quantity": quantity},
    )

    assert_error(
        add_product_response,
        404,
        f"Receipt with id {unknown_receipt_id} does not exist.",
    )


def test_should_close_receipt(
    client: TestClient, default_product: dict[str, Any]
) -> None:
    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": default_product["id"], "quantity": 2},
    )

    close_receipt_response = client.patch(
        f"/receipts/{receipt_id}", json={"status": "closed"}
    )

    assert close_receipt_response.status_code == 200
    assert close_receipt_response.json() == {}

    add_to_closed_receipt_response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": default_product["id"], "quantity": 1},
    )

    assert add_to_closed_receipt_response.status_code == 403

    assert_error(
        add_to_closed_receipt_response, 403, f"Receipt with id {receipt_id} is closed"
    )

    read_response = client.get(f"/receipts/{receipt_id}")

    assert read_response.status_code == 200
    retrieved_receipt = read_response.json()["receipt"]

    assert retrieved_receipt["status"] == "closed"


def test_should_delete_receipt(
    client: TestClient, default_product: dict[str, Any]
) -> None:
    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    delete_receipt_response = client.delete(f"/receipts/{receipt_id}")

    assert delete_receipt_response.status_code == 200
    assert delete_receipt_response.json() == {}

    read_response = client.get(f"/receipts/{receipt_id}")

    assert_error(read_response, 404, f"Receipt with id {receipt_id} does not exist.")


def test_should_not_delete_closed_receipt(
    client: TestClient, default_product: dict[str, Any]
) -> None:
    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    client.patch(f"/receipts/{receipt_id}", json={"status": "closed"})

    delete_closed_receipt_response = client.delete(f"/receipts/{receipt_id}")

    assert_error(
        delete_closed_receipt_response, 403, f"Receipt with id {receipt_id} is closed"
    )
