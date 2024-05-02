from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID, uuid4


@dataclass
class Unit:
    name: str
    id: UUID = field(default_factory=uuid4)


class UnitRepository(Protocol):
    def create(self, unit: Unit) -> None:
        pass

    def read(self, unit_id: UUID) -> Unit:
        pass

    def delete(self, unit_id: UUID) -> None:
        pass

    def read_all(self) -> list[Unit]:
        pass


class UnitExistsError(Exception):
    pass


class UnitDoesNotExistError(Exception):
    pass


@dataclass
class UnitService:
    units: UnitRepository

    def create_unit(self, name: str) -> Unit:
        try:
            unit_id = uuid4()
            unit = Unit(name, unit_id)
            self.units.create(unit)
            return unit
        except UnitExistsError as e:
            # aq iqneb ramenairi damatebiti damushaveba gvchirdeba
            raise e

    def fetch_unit(self, unit_id: UUID) -> Unit:
        try:
            return self.units.read(unit_id)
        except UnitDoesNotExistError as e:
            raise e

    def fetch_all_units(self) -> list[Unit]:
        return self.units.read_all()
