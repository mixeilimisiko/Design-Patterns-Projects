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
def fake_generator() -> FakeGenerator:
    return FakeGenerator(Faker())


def assert_error(response: Response, status_code: int, message: str) -> None:
    assert response.status_code == status_code
    assert "detail" in response.json()
    assert "error" in response.json()["detail"]
    assert message in response.json()["detail"]["error"]["message"]


def test_should_not_read_unknown_unit(
    client: TestClient, fake_generator: FakeGenerator
) -> None:
    unknown_id = uuid4()

    response = client.get(f"/units/{unknown_id}")

    assert_error(response, 404, f"Unit with id {unknown_id} does not exist.")


def test_should_create_unit(client: TestClient, fake_generator: FakeGenerator) -> None:
    unit_data = fake_generator.generate_unit_item(name="unit")

    response = client.post("/units", json=unit_data)

    assert response.status_code == 201
    assert "unit" in response.json()

    created_unit = response.json()["unit"]
    assert "id" in created_unit
    assert created_unit["name"] == unit_data["name"]


def test_should_not_create_duplicate_unit(
    client: TestClient, fake_generator: FakeGenerator
) -> None:
    unit_data = fake_generator.generate_unit_item(name="kg")

    response = client.post("/units", json=unit_data)

    assert response.status_code == 201
    assert "unit" in response.json()

    response = client.post("/units", json=unit_data)

    assert_error(response, 409, f"Unit with name '{unit_data['name']}' already exists")


def test_should_read_unit(client: TestClient, fake_generator: FakeGenerator) -> None:
    unit_data = fake_generator.generate_unit_item(name="liter")
    create_response = client.post("/units", json=unit_data)
    created_unit = create_response.json()["unit"]

    read_response = client.get(f"/units/{created_unit['id']}")

    assert read_response.status_code == 200
    assert "unit" in read_response.json()
    assert read_response.json()["unit"] == created_unit


def test_get_all_units_on_empty(client: TestClient) -> None:
    response = client.get("/units")

    assert response.status_code == 200
    assert response.json() == {"units": []}


def test_get_all_units(client: TestClient, fake_generator: FakeGenerator) -> None:
    unit_data = fake_generator.generate_unit_item(name="unit")

    create_response = client.post("/units", json=unit_data)
    assert create_response.status_code == 201
    created_unit = create_response.json()["unit"]
    assert "id" in created_unit
    assert created_unit["name"] == unit_data["name"]

    read_all_response = client.get("/units")
    assert read_all_response.status_code == 200
    retrieved_units = read_all_response.json()["units"]

    assert len(retrieved_units) == 1
    assert retrieved_units[0] == created_unit
