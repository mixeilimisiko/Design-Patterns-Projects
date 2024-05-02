from dataclasses import dataclass, field
from uuid import UUID

from core.units import Unit, UnitDoesNotExistError, UnitExistsError


@dataclass
class InMemoryUnits:
    units: dict[UUID, Unit] = field(default_factory=dict)

    def create(self, unit: Unit) -> None:
        for existing_unit in self.units.values():
            if existing_unit.name == unit.name:
                raise UnitExistsError(f"Unit with name '{unit.name}' already exists")

        self.units[unit.id] = unit
        for unit in self.units.values():
            print(unit.name)

    def read(self, unit_id: UUID) -> Unit:
        try:
            return self.units[unit_id]
        except KeyError:
            raise UnitDoesNotExistError(f"Unit with id '{unit_id}' does not exist")

    def delete(self, unit_id: UUID) -> None:
        try:
            del self.units[unit_id]
        except KeyError:
            raise UnitDoesNotExistError(f"Unit with id '{unit_id}' does not exist")

    def read_all(self) -> list[Unit]:
        return list(self.units.values())
