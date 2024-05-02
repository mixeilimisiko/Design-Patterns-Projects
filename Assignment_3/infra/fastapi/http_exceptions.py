from uuid import UUID

from fastapi import HTTPException
from starlette import status


class CreateUnitExceptionResponse(HTTPException):
    def __init__(self, name: str) -> None:
        detail = {"error": {"message": f"Unit with name '{name}' already exists"}}
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# class ReadUnitExceptionResponse(HTTPException):
#     def __init__(self, unit_id: UUID) -> None:
#         detail = {"error": {"message": f"Unit with id {unit_id} does not exist"}}
#         super().__init__(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=detail,
#         )


class CreateProductExceptionResponse(HTTPException):
    def __init__(self, barcode: str):
        detail = {
            "error": {"message": f"Product with barcode '{barcode}' already exists"}
        }
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# class ProductExistsErrorResponse(HTTPException):
#     def __init__(self, product_id: UUID):
#         detail = {
#         "error": {"message": f"Product with id<{product_id}> does not exist"}
#         }
#         super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
#
#
# class ReceiptDoesNotExistResponse(HTTPException):
#     def __init__(self, receipt_id: UUID) -> None:
#         detail = {
#         "error": {"message": f"Receipt with id {receipt_id} does not exist."}
#         }
#         super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
#
#
# class ExistsErrorResponse(HTTPException):
#     def __init__(self, item_type: str, item_id: UUID):
#         detail = {
#             "error": {"message": f"{item_type} with id<{item_id}> does not exist"}
#         }
#         super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class DoesNotExistResponse(HTTPException):
    def __init__(self, item_type: str, item_id: UUID) -> None:
        detail = {
            "error": {"message": f"{item_type} with id {item_id} does not exist."}
        }
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
