from uuid import UUID, uuid4

import pytest

from core.units import UnitDoesNotExistError, UnitExistsError
from infra.repos.in_memory.in_memory_units import InMemoryUnits
from tests.fake_generator import FakeGenerator


@pytest.fixture
def fake_generator() -> FakeGenerator:
    return FakeGenerator()


def test_should_create_unit(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    fake_unit = fake_generator.generate_unit()

    unit_repository.create(fake_unit)
    assert unit_repository.read(fake_unit.id) == fake_unit


def test_should_not_create_duplicate_unit(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    fake_unit1 = fake_generator.generate_unit()
    fake_unit2 = fake_generator.generate_unit(name=fake_unit1.name)

    unit_repository.create(fake_unit1)

    with pytest.raises(UnitExistsError):
        unit_repository.create(fake_unit2)


def test_should_read_unit(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    fake_unit = fake_generator.generate_unit()

    unit_repository.create(fake_unit)
    retrieved_unit = unit_repository.read(fake_unit.id)
    assert retrieved_unit == fake_unit


def test_should_not_read_nonexistent_unit(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    unknown_unit_id: UUID = uuid4()

    with pytest.raises(UnitDoesNotExistError):
        unit_repository.read(unknown_unit_id)


def test_should_delete_unit(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    fake_unit = fake_generator.generate_unit()

    unit_repository.create(fake_unit)
    unit_repository.delete(fake_unit.id)

    with pytest.raises(UnitDoesNotExistError):
        unit_repository.read(fake_unit.id)


def test_should_not_delete_nonexistent_unit(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    unknown_unit_id: UUID = uuid4()

    with pytest.raises(UnitDoesNotExistError):
        unit_repository.delete(unknown_unit_id)


def test_should_read_all_units(fake_generator: FakeGenerator) -> None:
    unit_repository = InMemoryUnits()
    fake_unit1 = fake_generator.generate_unit()
    fake_unit2 = fake_generator.generate_unit()

    unit_repository.create(fake_unit1)
    unit_repository.create(fake_unit2)

    all_units = unit_repository.read_all()
    assert fake_unit1 in all_units
    assert fake_unit2 in all_units
