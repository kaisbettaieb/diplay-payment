import pandas as pd

from src.utils import read_data


def test_utils_read_data(mocker):
    df = pd.DataFrame({"customer_id": [1, 2], "email": ["jdoe@gmail.com", ""]})
    mocker.patch("src.utils.pd.read_csv",
                 return_value=df)

    assert read_data("customers.csv").equals(df)


def test_utils_read_data_exception(mocker):
    mocker.patch("src.utils.pd.read_csv",
                 side_effect=FileNotFoundError("File not found"))

    assert read_data("customers.csv").empty
