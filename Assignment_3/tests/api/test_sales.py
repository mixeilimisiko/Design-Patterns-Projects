import pytest
from faker import Faker
from fastapi.testclient import TestClient

from runner.setup import init_app
from tests.fake_generator import FakeGenerator


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app())


@pytest.fixture
def fake_generator(client: TestClient) -> FakeGenerator:
    return FakeGenerator(Faker())


def test_sales_report(client: TestClient, fake_generator: FakeGenerator) -> None:
    unit_data = fake_generator.generate_unit_item(name="kg")
    create_unit_response = client.post("/units", json=unit_data)
    assert create_unit_response.status_code == 201
    kg_unit = create_unit_response.json()["unit"]

    product_data = fake_generator.generate_product_item(unit_id=kg_unit["id"])
    price = product_data["price"]
    create_product_response = client.post("/products", json=product_data)
    assert create_product_response.status_code == 201
    default_product = create_product_response.json()["product"]

    create_receipt_response = client.post("/receipts")
    receipt_id = create_receipt_response.json()["receipt"]["id"]

    quantity = 3
    add_product_response = client.post(
        f"/receipts/{receipt_id}/products",
        json={"id": default_product["id"], "quantity": quantity},
    )
    assert add_product_response.status_code == 201

    close_receipt_response = client.patch(
        f"/receipts/{receipt_id}", json={"status": "closed"}
    )
    assert close_receipt_response.status_code == 200

    sales_report_response = client.get("/sales")
    assert sales_report_response.status_code == 200
    sales_report = sales_report_response.json()["sales"]

    assert "n_receipts" in sales_report
    assert "revenue" in sales_report

    assert sales_report["n_receipts"] == 1
    assert sales_report["revenue"] == 3 * price


def test_should_return_empty_report(client: TestClient) -> None:
    sales_report_response = client.get("/sales")
    assert sales_report_response.status_code == 200
    sales_report = sales_report_response.json()["sales"]

    assert "n_receipts" in sales_report
    assert "revenue" in sales_report

    assert sales_report["n_receipts"] == 0
    assert sales_report["revenue"] == 0
