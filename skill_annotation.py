"""
Module containing functions that map skills to green activities.
"""
from pathlib import Path
from typing import Optional, Union
import time as t
import pandas as pd

def match_skill_to_green_type(skill_data: pd.Series, job_listing: pd.Series) -> Union[str, int]:
    """return green category of the job if it matches the skill, otherwise return 0.

    Args:
        skill_data: pd.Series, row containing information about the skill.
        job_listing: pd.Series, row containing information about the job listing.

    Returns:
        Union[str, int], str indicating the green category if skill present in listing, else 0.
    """
    skill_col = job_listing[skill_data["category"]]

    if skill_data["skill_name"] in skill_col:
        if pd.isna(job_listing["Green Category"]):
            return 0
        return job_listing["Green Category"]
    return 0


def count_matches(
    skill_data: pd.Series,
    green_categories: list[str],
    listing_data: pd.DataFrame,
    verbose: Optional[int] = 1
) -> list[int]:
    """Function to count how often each green category is matched to a given skill

    Args:
        skill_data: pd.Series, row containing information about the skill.
        green_categories: list[str], string values of all possible green categories.
        listing_data: pd.DataFrame, table containing all selected listings.
        verbose: Optional[int], set to 0 to supress print statements.

    Returns:
        list[int], counts of each green category matched to the skill.
    """
    if verbose > 0:
        print(skill_data["skill_name"])
    matches = listing_data.apply(lambda y: match_skill_to_green_type(skill_data, y), axis=1)
    return [len(matches[matches == green_category]) for green_category in green_categories]



def map_skills_to_green_type(
    skill_df: pd.DataFrame,
    listing_df: pd.DataFrame,
    load_new: Optional[bool] = False,
    verbose: Optional[int] = 1
) -> pd.DataFrame:
    """Function to map supplied skills to green categories and store an annotated df.

    Args:
        skill_df: pd.DataFrame, contains list of all skills, skill types and occurrences.
        listing_df: pd.DataFrame, contains all job listings & their potential green categories
        load_new: Optional[bool], whether to regenerate the annotated df or to read from file.
        verbose: Optional[int], set to 0 to suppress print statements.

    Returns:
        pd.DataFrame, skill_df with annotations of green category counts.
    """

    annotated_path = Path("_data") / "annotated_skills.csv"
    if not load_new and annotated_path.exists():
        return pd.read_csv(annotated_path)

    green_categories = (
        "Green Enhanced Skills",
        "Green New and Emerging",
        "Green Increased Demand",
        "Not Green"
    )

    listing_df["Green Category"].fillna(green_categories[3], inplace=True)

    start = t.time()
    green_cat_to_skills = skill_df.apply(
        lambda skill: count_matches(skill, green_categories, listing_df, verbose=verbose),
        axis=1
    )
    if verbose > 0:
        print(t.time() - start)
    for i, cat in enumerate(green_categories):
        skill_df[cat] = green_cat_to_skills.map(lambda x, i=i: x[i])

    skill_df.to_csv(annotated_path, index=False)
    return skill_df
