from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_app():
    result = runner.invoke(app, ["customers.csv", "purchases.csv", ])
    assert "Processing customers data" in result.stdout
