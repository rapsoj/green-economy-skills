from pathlib import Path

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import geopandas as gp
import pandas as pd

from load_data import get_merged_data, load_green_category


mpl.use("TkAgg")

NUTS_NAME = "hex_scaled_uk.shp"
JOBS_BY_NUTS = "4digitoccupationbyvariousfactorsjd19.xlsx"

GREEN_CATEGORIES = [
    "Green Enhanced Skills",
    "Green Increased Demand",
    "Green New and Emerging"
]


def reshape_to_nuts(df):
    counts = df.iloc[:, :-3].sum(axis=0)

    counts = counts.reset_index()

    counts.columns = ["NUTS", "Counts"]

    counts["NUTS_ID"] = counts["NUTS"].map(lambda x: x.split(" ")[0])
    counts["NUTS_NAME"] = counts["NUTS"].map(lambda x: x.split(" ")[1])
    return counts


def plot_map(df, counts_df, axis, index):
    df.plot(color="lightgrey", ax=ax)

    df = df.merge(counts_df, left_on="NUTS_NAME", right_on="NUTS_NAME", how="left")

    df["Counts"] *= 100

    kwargs = {
        "cmap": "Greens",
        "ax": ax,
        "vmin": 0,
        "vmax": 20
    }

    df.plot("Counts", **kwargs)



if __name__ == "__main__":
    jobs_by_region = pd.read_excel(Path("_data") /JOBS_BY_NUTS, sheet_name=4, skiprows=8)
    del jobs_by_region["Unnamed: 0"]
    jobs_by_region = jobs_by_region[~jobs_by_region["Unnamed: 1"].isna()]
    jobs_by_region["SOC_CODE"] = jobs_by_region["Unnamed: 1"].map(lambda x: x.split()[0]).astype(int)
    jobs_by_region["SOC_NAME"] = jobs_by_region["Unnamed: 1"].map(lambda x: x.split("'")[1]).astype(str)
    del jobs_by_region["Unnamed: 1"]

    jobs_by_region.replace("*", 0, inplace=True)
    jobs_by_region.replace("-", 0, inplace=True)

    green_categories = load_green_category()
    del green_categories["SOC2010 Unit Group Titles"]

    jobs_by_region = jobs_by_region.merge(green_categories, left_on="SOC_CODE", right_on="SOC2010 4-digit", how="left")

    del jobs_by_region["SOC2010 4-digit"]

    for col in jobs_by_region:
        if col.startswith("UK"):
            jobs_by_region[col] = jobs_by_region[col].astype(float)

    counts = reshape_to_nuts(jobs_by_region)
    green_counts = reshape_to_nuts(jobs_by_region[jobs_by_region["Green Category"].isin(GREEN_CATEGORIES)])
    green_counts["Counts"] /= counts["Counts"]

    green_dataframes = [green_counts]

    for green_cat in GREEN_CATEGORIES:
        cat_counts = reshape_to_nuts(jobs_by_region[jobs_by_region["Green Category"] == green_cat])
        cat_counts["Counts"] /= counts["Counts"]
        green_dataframes.append(cat_counts)

    nuts_regions = gp.read_file(Path("_data") / NUTS_NAME / NUTS_NAME)


    nuts_regions = nuts_regions[nuts_regions["CNTR_CODE"] == "UK"]
    nuts_regions = nuts_regions[nuts_regions["LEVL_CODE"] == 3]

    fig = plt.figure()
    axes = fig.subplots(1, 3).flat
    titles = GREEN_CATEGORIES
    for i, ax in enumerate(axes):
        ax.set_title(titles[i], fontsize=20)
        plot_map(nuts_regions, green_dataframes[1:][i], ax, i)
        ax.set_axis_off()
    plt.show()