"""
Helper functions to load the datasets used in the project.
"""
from pathlib import Path
from typing import Optional

import pandas as pd

from util import get_unique_skills

def load_lightcast_data(path: Optional[str] = None) -> pd.DataFrame:
    """Function to load lightcast dataset.

    Args:
        path: Optional[str], override default path "_data/Lightcast, UK Postings Sample.csv"

    Returns:
        pd.DataFrame, the dataframe loaded from the file, excluding any rows with NA index.
    """

    if path is None:
        path = Path("_data") / "Lightcast, UK Postings Sample.csv"

    lightcast_df = pd.read_csv(path, index_col=0, low_memory=False)

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


def load_green_category(path: Optional[str] = None) -> pd.DataFrame:
    """Helper to load file of green category data.

    Args:
        path: Optional[str], override default path "green_jobs.xlsx"

    Returns:
        pd.DataFrame, loaded and barely cleaned data.
    """

    if path is None:
        path = Path("green_jobs.xlsx")

    green_jobs_df = pd.read_excel(path)

    return green_jobs_df


def get_merged_data(load_new: Optional[bool] = False) -> pd.DataFrame:
    """Function to load lightcast & greentimeshare data and merge the two dfs.

    Args:
        load_new: Optional[bool], whether to regenerate data file if it already exists.

    Returns:
        pd.DataFrame containing merged lightcast and greentimeshare data.
    """
    merged_path = Path("_data") / "merged_data.csv"
    if not load_new and merged_path.exists():
        return pd.read_csv(merged_path)

    lc_data = load_lightcast_data()
    lc_data = lc_data[~lc_data["SOC_4"].isna()]
    greents_data = load_greentimeshare()
    green_category = load_green_category()
    joint_data = lc_data.merge(greents_data, left_on="SOC_4", right_on="SOC 2010 code", how="left")
    joint_data = joint_data.merge(
        green_category,
        left_on="SOC_4",
        right_on="SOC2010 4-digit",
        how="left"
    )
    del joint_data["SOC2010 Unit Group Titles"]
    del joint_data["SOC2010 4-digit"]
    del joint_data["SOC 2010 code"]
    del joint_data["SOC 2010 description"]

    joint_data["percentage"] = joint_data["2019"]

    joint_data.to_csv(merged_path)

    return joint_data


def get_skills_key(load_new: Optional[bool] = False) -> pd.DataFrame:
    """Function to extract skill names, counts and categories from Lightcast.

    Args:
        load_new: Optional[bool], whether to regenerate data file if it already exists.

    Returns:
        pd.DataFrame containing skill names, occurrences, and categories.
    """

    skills_path = Path("_data") / "skills_key.csv"
    if not load_new and skills_path.exists():
        return pd.read_csv(skills_path)

    lightcast_df = load_lightcast_data()

    hard_df = get_unique_skills(lightcast_df["SPECIALIZED_SKILLS_NAME"], "specialized")
    soft_df = get_unique_skills(lightcast_df["COMMON_SKILLS_NAME"], "common")
    coding_df = get_unique_skills(lightcast_df["SOFTWARE_SKILLS_NAME"], "software")

    skills_df = pd.concat([hard_df, soft_df, coding_df])

    skills_df.to_csv(skills_path, index=False)

    return skills_df
