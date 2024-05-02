import os

from fastapi import FastAPI

from core.products import ProductRepository, ProductService
from core.receipts import ReceiptRepository, ReceiptService
from core.units import UnitRepository, UnitService
from infra.fastapi.products import product_api
from infra.fastapi.receipts import receipt_api
from infra.fastapi.sales import sales_api
from infra.fastapi.units import unit_api
from infra.repos.in_memory.in_memory_products import InMemoryProducts
from infra.repos.in_memory.in_memory_receipts import InMemoryReceipts
from infra.repos.in_memory.in_memory_units import InMemoryUnits
from infra.repos.sqlite.db_manager import DbManager


def init_app() -> FastAPI:
    app = FastAPI()
    app.include_router(unit_api)
    app.include_router(product_api)
    app.include_router(receipt_api)
    app.include_router(sales_api)

    if os.getenv("REPOSITORY_KIND", "memory") == "sqlite":
        # print("X")
        db_manager = DbManager()
        # db_manager.drop_tables()
        # db_manager.create_tables()
        units: UnitRepository = db_manager.get_unit_repository()
        products: ProductRepository = db_manager.get_product_repository()
        receipts: ReceiptRepository = db_manager.get_receipt_repository()
        app.state.unit_service = UnitService(units)
        app.state.product_service = ProductService(products=products, units=units)
        app.state.receipt_service = ReceiptService(products=products, receipts=receipts)
    else:
        units = InMemoryUnits()
        products = InMemoryProducts()
        receipts = InMemoryReceipts()
        app.state.unit_service = UnitService(units)
        app.state.product_service = ProductService(products=products, units=units)
        app.state.receipt_service = ReceiptService(products=products, receipts=receipts)

    # db_manager = DbManager()
    # # db_manager.drop_tables()
    # # db_manager.create_tables()
    # units = db_manager.get_unit_repository()
    # products = db_manager.get_product_repository()
    # receipts = db_manager.get_receipt_repository()
    # app.state.unit_service = UnitService(units)
    # app.state.product_service = ProductService(products=products, units=units)
    # app.state.receipt_service = ReceiptService(products=products, receipts=receipts)

    return app
