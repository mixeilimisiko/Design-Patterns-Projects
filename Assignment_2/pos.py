import typer

from db_init import BatchRepositoryInitializer, DiscountInitializer, ItemInitializer
from pos_simulator import PosSimulator
from printer import Printer
from real_database import SQLiteDBCreator

app = typer.Typer()


@app.command()
def list() -> None:
    typer.echo("Printing information of the store...")
    db_creator = SQLiteDBCreator()
    db_creator.drop_tables()
    db_creator.create_tables()
    item_repo = ItemInitializer.initialize_item_repository(inmemory=False)
    batch_repo = BatchRepositoryInitializer.initialize_batch_repository(item_repo, inmemory=False)
    discount_repo = DiscountInitializer.initialize_discount_repository()
    Printer.print_items(item_repo)
    Printer.print_batches(batch_repo)
    Printer.print_discounts(discount_repo)


@app.command()
def simulate() -> None:
    typer.echo("Starting simulation...")

    db_creator = SQLiteDBCreator()
    db_creator.drop_tables()
    db_creator.create_tables()
    item_repo = ItemInitializer.initialize_item_repository(inmemory=False)
    batch_repo = BatchRepositoryInitializer.initialize_batch_repository(item_repo, inmemory=False)
    discount_repo = DiscountInitializer.initialize_discount_repository(inmemory=False)
    simulator = PosSimulator(item_repo, discount_repo, batch_repo)
    simulator.setup()
    simulator.simulate()

    typer.echo("Simulation completed.")


if __name__ == "__main__":
    app()
