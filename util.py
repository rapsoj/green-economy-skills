"""
File containing random helper functions.
"""
import ast
import numpy as np
import pandas as pd

def get_unique_skills(column: pd.Series, category_name: str):
    """Helper to find unique set of skills.

    Args:
        column: pd.Series, column containing string formatted list of skills.
        category_name: str, category to associate with skills.

    Returns:
        pd.DataFrame containing skills in this category, counts, and name of the category.
    """
    skill_list = []

    column.map(lambda x: skill_list.extend([n.strip() for n in ast.literal_eval(x)]))

    uniques, counts = np.unique(skill_list, return_counts=True)

    return pd.DataFrame({
        "skill_name": uniques,
        "occurrences": counts,
        "category": np.repeat(category_name, uniques.shape)
    })
