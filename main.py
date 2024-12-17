import logging
import os
from typing import Annotated, Optional
import typer
from typer import Argument, Option

from src.utils import read_data
from src.core import map_purchases, send_bills, Observer, create_bills

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def payment(customers: Annotated[str, Argument(help="Path to the csv file of customers details")],
            purchases: Annotated[str, Argument(help="Path to the csv file of customers purchases history")],
            url: Annotated[Optional[str], Option(help="URL of Display endpoint to send customer purchases,"
                                                      " defaults to environment variable API_URL")] = None):
    observer = Observer()

    typer.echo("Processing customers data...")

    customers_details = read_data(customers)
    if customers_details.empty:
        observer.add(f"Failed to read customers data from  {customers}, file may not be present", level="error", filepath=customers)
        observer.report()
        return

    purchases_details = read_data(purchases)

    if purchases_details.empty:
        observer.add(f"Failed to read customers purchases data from {purchases}, file may not be present",
                     level="error", filepath=purchases)
        observer.report()
        return

    purchases_by_customers = map_purchases(customers_details, purchases_details, observer)

    typer.echo("Creating bill...")

    invoice = create_bills(customers_details, purchases_by_customers, observer)

    typer.echo("Sending customers purchases to API...")
    if not url:
        typer.echo("No Display url is provided, defaulting to environment variable API_URL")
        url = os.getenv("API_URL")
    status = send_bills(invoice, url, observer)

    if status:
        typer.echo("Successfully sent the invoice for payment processing")
    else:
        typer.echo("Failed to send the invoice for payment processing ")

    observer.report()


if __name__ == "__main__":
    app()
