import sqlite3
from dataclasses import dataclass
from uuid import UUID

from core.units import Unit, UnitDoesNotExistError, UnitExistsError


@dataclass
class SQLiteUnits:
    db_name: str

    def create(self, unit: Unit) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            try:
                cursor.execute(
                    "INSERT INTO units (id, name) VALUES (?, ?)",
                    (str(unit.id), unit.name),
                )
            except sqlite3.IntegrityError:
                raise UnitExistsError(f"Unit with name '{unit.name}' already exists")

    def read(self, unit_id: UUID) -> Unit:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM units WHERE id = ?", (str(unit_id),))
            result = cursor.fetchone()

            if result is None:
                raise UnitDoesNotExistError(f"Unit with id '{unit_id}' does not exist")

            return Unit(id=UUID(result[0]), name=result[1])

    def delete(self, unit_id: UUID) -> None:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM units WHERE id = ?", (str(unit_id),))

            if cursor.rowcount == 0:
                raise UnitDoesNotExistError(f"Unit with id '{unit_id}' does not exist")

    def read_all(self) -> list[Unit]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM units")
            results = cursor.fetchall()

            return [Unit(id=UUID(result[0]), name=result[1]) for result in results]
