import logging

import pandas as pd

logger = logging.getLogger(__name__)


def read_data(path: str) -> pd.DataFrame:
    """
    Return the content of csv file from path in dataframe
    :param path: str: Path to the file
    :return: DataFrame
    """
    try:
        return pd.read_csv(path, delimiter=";")
    except FileNotFoundError:
        return pd.DataFrame()
