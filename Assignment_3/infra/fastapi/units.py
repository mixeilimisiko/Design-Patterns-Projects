from uuid import UUID

from fastapi import APIRouter, status
from pydantic import BaseModel

from core.units import Unit, UnitDoesNotExistError, UnitExistsError
from infra.fastapi.dependables import UnitServiceDependable
from infra.fastapi.http_exceptions import (
    CreateUnitExceptionResponse,
    DoesNotExistResponse,
)

unit_api = APIRouter(tags=["Units"])


class CreateUnitRequest(BaseModel):
    name: str


class UnitItem(BaseModel):
    id: UUID
    name: str


class UnitEnvelope(BaseModel):
    unit: UnitItem


class FetchUnitsResponse(BaseModel):
    units: list[Unit]


@unit_api.post(
    "/units",
    status_code=status.HTTP_201_CREATED,
    response_model=UnitEnvelope,
)
def create_unit(
    request: CreateUnitRequest, unit_service: UnitServiceDependable
) -> dict[str, UnitItem]:
    try:
        created_unit: Unit = unit_service.create_unit(request.name)
        return {"unit": UnitItem(id=created_unit.id, name=created_unit.name)}
    except UnitExistsError as e:
        # print(e)
        raise CreateUnitExceptionResponse(request.name) from e


@unit_api.get("/units/{unit_id}", response_model=UnitEnvelope)
def fetch_unit(
    unit_id: UUID, unit_service: UnitServiceDependable
) -> dict[str, UnitItem]:
    try:
        unit: Unit = unit_service.fetch_unit(unit_id)
        return {"unit": UnitItem(id=unit.id, name=unit.name)}
    except UnitDoesNotExistError as e:
        raise DoesNotExistResponse(item_type="Unit", item_id=unit_id) from e


@unit_api.get("/units", response_model=FetchUnitsResponse)
def fetch_all(unit_service: UnitServiceDependable) -> FetchUnitsResponse:
    units = unit_service.fetch_all_units()
    return FetchUnitsResponse(units=units)
