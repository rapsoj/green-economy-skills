"""
Helper functions to load the datasets used in the project.
"""
from pathlib import Path
from typing import Optional

import pandas as pd

def load_lightcast_data(path: Optional[str] = None) -> pd.DataFrame:
    """Function to load lightcast dataset.

    Args:
        path: Optional[str], override default path "_data/Lightcast, UK Postings Sample.csv"

    Returns:
        pd.DataFrame, the dataframe loaded from the file, excluding any rows with NA index.
    """

    if path is None:
        path = Path("_data") / "Lightcast, UK Postings Sample.csv"

    lightcast_df = pd.read_csv(path, index_col=0)

    # drop na indices
    lightcast_df = lightcast_df[~lightcast_df.index.isna()]
    lightcast_df.index = lightcast_df.index.astype(int)  # set index to int

    return lightcast_df


def load_greentimeshare(path: Optional[str] = None) -> pd.DataFrame:
    """Function to load the greentimesharesoc.xlsx file.

    Args:
        path: Optional[str], override default path "greentimesharesoc.xlsx"

    Returns:
        pd.DataFrame, loaded and barely cleaned data.
    """

    if path is None:
        path = Path("greentimesharesoc.xlsx")

    greents_df = pd.read_excel(path, skiprows=2, sheet_name=3)

    return greents_df


def get_merged_data() -> pd.DataFrame:
    """Function to load lightcast & greentimeshare data and merge the two dfs.

    Returns:
        pd.DataFrame containing merged lightcast and greentimeshare data.
    """
    lc_data = load_lightcast_data()
    lc_data = lc_data[~lc_data["SOC_4"].isna()]
    greents_data = load_greentimeshare()
    joint_data = lc_data.merge(greents_data, left_on="SOC_4", right_on="SOC 2010 code", how="inner")
    del joint_data["SOC 2010 code"]
    del joint_data["SOC 2010 description"]

    joint_data["percentage"] = joint_data["2019"]

    return joint_data
