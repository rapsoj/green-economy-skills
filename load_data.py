"""
Helper functions to load the datasets used in the project.
"""
from pathlib import Path
from typing import Optional
import time as t

from tqdm import tqdm
import pandas as pd
import numpy as np


def load_lightcast_data(path: Optional[str] = None) -> pd.DataFrame:
    """Function to load lightcast dataset.

    Args:
        path: Optional[str], override default path "_data/Lightcast, UK Postings Sample.csv"

    Returns:
        pd.DataFrame, the dataframe loaded from the file, excluding any rows with NA index.
    """

    if path is None:
        path = Path("_data") / "Lightcast, UK, Postings Sample, 1m, Main.csv"

    lightcast_df = pd.read_csv(path, low_memory=False)

    # drop na indices
    lightcast_df = lightcast_df[~lightcast_df["ID"].isna()]

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


def load_skills_to_jobs(
    path: Optional[str] = None,
    usecols: Optional[list[str]] = None
) -> pd.DataFrame:
    """Helper to load skills to jobs data.

    Args:
        path: Optional[str], override default path
            "_data/Lightcast, UK Postings Sample, 1m, Skills.csv"
        usecols: Optional[list[str]], select columns to load

    Returns:
        pd.DataFrame, loaded and barely cleaned data.
    """

    if path is None:
        path = Path("_data") / "Lightcast, UK Postings Sample, 1m, Skills.csv"

    if usecols is not None:
        return pd.read_csv(path, usecols=usecols)
    return pd.read_csv(path)

def get_merged_data(
    load_new: Optional[bool] = False,
    usecols: Optional[list[str]] = None
) -> pd.DataFrame:
    """Function to load lightcast & greentimeshare data and merge the two dfs.

    Args:
        load_new: Optional[bool], whether to regenerate data file if it already exists.

    Returns:
        pd.DataFrame containing merged lightcast and greentimeshare data.
    """
    merged_path = Path("_data") / "merged_data.csv"
    if not load_new and merged_path.exists():
        if usecols is not None:
            return pd.read_csv(merged_path, usecols=usecols)
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

    joint_data.to_csv(merged_path, index=False)

    if usecols is not None:
        return joint_data.loc[:, usecols]

    return joint_data


def get_skills_key(
    load_new: Optional[bool] = False,
) -> pd.DataFrame:
    """Function to extract skill names, counts and categories from Lightcast.

    Args:
        load_new: Optional[bool], whether to regenerate data file if it already exists.

    Returns:
        pd.DataFrame containing skill names, occurrences, and categories.
    """

    skills_path = Path("_data") / "skills_key.csv"
    if not load_new and skills_path.exists():
        return pd.read_csv(skills_path)

    lightcast_df = load_skills_to_jobs()

    unique_skills, indices, counts = np.unique(
        lightcast_df["SKILL_NAME"],
        return_index=True,
        return_counts=True
    )

    skills_df = pd.DataFrame({
        "Name": unique_skills,
        "Subcategory": lightcast_df["SKILL_SUBCATEGORY_NAME"].iloc[indices],
        "Category": lightcast_df["SKILL_CATEGORY_NAME"].iloc[indices],
        "Type": lightcast_df["SKILL_TYPE"].iloc[indices],
        "IsSoftware": lightcast_df["IS_SOFTWARE"].iloc[indices],
        "Counts": counts
    }).sort_values(by="Name")

    skills_df.to_csv(skills_path, index=False)

    return skills_df


def get_annotated_skills(load_new: Optional[bool] = False) -> pd.DataFrame:
    """Function to annotate skill names with green categories.

    Args:
        load_new: Optional[bool], whether to regenerate data file if it already exists.

    Returns:
        pd.DataFrame containing the annotated skills.
    """
    annotated_skills_path = Path("_data") / "annotated_skills.csv"
    if not load_new and annotated_skills_path.exists():
        return pd.read_csv(annotated_skills_path, index=0)
    print("Loading data...")
    start = t.time()
    skills_key = get_skills_key()
    skills_to_jobs = load_skills_to_jobs(usecols=["ID", "SKILL_NAME"])
    green_category_map = get_merged_data(usecols=["ID", "Green Category"])
    green_category_map = green_category_map[~green_category_map["Green Category"].isna()]
    skills_to_jobs = skills_to_jobs[skills_to_jobs["ID"].isin(green_category_map["ID"])]
    green_category_map.set_index("ID", inplace=True)
    step_1_time = t.time()
    print(f"Done loading data in {round(step_1_time - start, 2)}s!")

    print("Annotating skills with green categories...")
    tqdm.pandas()
    skills_to_jobs["Green Category"] = skills_to_jobs["ID"].progress_map(
        lambda x: green_category_map.loc[int(x), "Green Category"]
    )

    step_2_time = t.time()
    print(f"Done annotating skills in {round(step_2_time - step_1_time, 2)}s!")


    skills_to_green_category = (
        skills_to_jobs
        .loc[:, ["SKILL_NAME", "Green Category"]]
        .groupby('SKILL_NAME')
        .value_counts(sort=False)
    )

    skills_to_green_category = skills_to_green_category.reset_index()
    print(skills_to_green_category.head())


    def extract_from_nested_index(skill_name: str, category: str):
        subset = skills_to_green_category[skills_to_green_category["SKILL_NAME"] == skill_name]
        value = subset[subset["Green Category"] == category]

        if len(value) == 0:
            return 0
        return value.iloc[0, 2]

    print("Adding annotations to skill key...")
    for cat in np.unique(green_category_map["Green Category"]):
        print(f"\tAdding column {cat}...")
        t.sleep(.1)
        tqdm.pandas()
        skills_key[cat] = (
            skills_key["Name"]
            .progress_apply(
                lambda x, category=cat: extract_from_nested_index(x, category)
            )
        )
        print("\tDone!")
    print(f"Done annotating skill key in {round(t.time() - step_2_time, 2)}s!")

    print(skills_key.loc[:, [
                                "Name",
                                "Green New and Emerging",
                                "Green Increased Demand",
                                "Green Enhanced Skills"
                            ]].head())
    skills_key.to_csv(annotated_skills_path)
    return skills_key
