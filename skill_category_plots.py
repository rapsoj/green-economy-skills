from pathlib import Path
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from load_data import get_annotated_skills

mpl.use("TkAgg")


if __name__ == "__main__":

    skills = get_annotated_skills()

    skills_by_category = (
        skills
        .loc[:, [
            "Category",
            "Counts",
            "Green Enhanced Skills",
            "Green Increased Demand",
            "Green New and Emerging"
        ]]
        .groupby("Category")
        .sum()
    )

    """    skills_by_category.loc[:, :] = (
            skills_by_category.values /
            skills_by_category["Counts"].values[..., np.newaxis]
        )"""

    skills_by_category["Green"] = skills_by_category["Green New and Emerging"] + skills_by_category["Green Increased Demand"] + skills_by_category["Green Enhanced Skills"]
    skills_by_category["Not Green"] = skills_by_category["Counts"] - skills_by_category["Green"]


    for col in skills_by_category.columns:
        if col == "Counts":
            continue
        print(f"\n\nMost {col}:")
        sorted_skill = skills_by_category.loc[:, col].sort_values(ascending=False)
        print(sorted_skill.head())

    fig, axes = plt.subplots(2, 5, figsize=(10, 5))
    axes = axes.flat
    fig.suptitle("Skills Categories by Frequency and Green Fraction", size=20)

    max_count = skills_by_category["Counts"].max()

    skills_by_category["Green Fraction"] = skills_by_category["Green"] / skills_by_category["Counts"]

    skills_by_category.sort_values(by="Green Fraction", inplace=True, ascending=False)

    skills_by_category.to_csv(Path("_data") / "skills_by_cat_green_frac.csv")

    legend_items = []

    biggest_cats = skills_by_category.sort_values(by="Counts", ascending=False).iloc[:5, :]
    biggest_labels = biggest_cats.index.values

    for i, (label, data_row) in enumerate(skills_by_category.iterrows()):
        if i >= 5 and label not in biggest_labels:
            continue
        elif i >= 5:
            k = list(biggest_labels).index(label) + 4
        else:
            k = i
        ax = axes[k]
        ax.set_aspect("equal")
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_title(" & \n".join(",\n".join(label.split(", ")).split(" and ")), fontsize=15)

        radius = (data_row["Counts"] / max_count) ** .5

        background = mpatches.Circle((0, 0), radius=radius, color="lightgrey")

        ax.add_artist(
            background
        )

        if k == 0:
            legend_items.append(background)
        left = 0
        colors = ["green", "forestgreen", "limegreen"]
        for j, green_cat in enumerate([
            "Green Enhanced Skills",
            "Green Increased Demand",
            "Green New and Emerging"
        ]):
            right = left + (360 * data_row[green_cat] / data_row["Counts"])
            print(left, right, green_cat)
            wedge = mpatches.Wedge((0, 0), radius, left, right, color=colors[j])
            if k == 0:
                legend_items.append(wedge)
            ax.add_artist(
                wedge
            )
            left = right
        ax.set_axis_off()

    axes[-1].set_axis_off()

    fig.legend(legend_items, [
        "Not Green",
        "Green (Enh. Skills)",
        "Green (Incr. Demand)",
        "Green (New & Emerging)"
    ], loc="lower right", fontsize=12)

    plt.show()