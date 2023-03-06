from pathlib import Path

from load_data import get_annotated_skills

GREEN_CATEGORIES = [
    "Green Enhanced Skills",
    "Green Increased Demand",
    "Green New and Emerging"
]


if __name__ == "__main__":

    annotated_skills = get_annotated_skills()
    annotated_skills = annotated_skills.loc[:, ["Counts", "Subcategory"] + GREEN_CATEGORIES].groupby("Subcategory").sum()

    annotated_skills["Green"] = sum(annotated_skills[cat] for cat in GREEN_CATEGORIES)

    annotated_skills["Green %"] = 100 * annotated_skills["Green"] / annotated_skills["Counts"]

    annotated_skills.sort_values(by="Green %", ascending=False, inplace=True)

    annotated_skills.to_csv(Path("_data") / "subcategories_by_green_percentage.csv")
