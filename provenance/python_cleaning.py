import pandas as pd
import numpy as np
from pandasql import sqldf

pysqldf = lambda q: sqldf(q, globals())


# @BEGIN main
# @PARAM db_pth
# @IN input_data  @URI file:{db_pth}/ppp_data_after_openrefine.csv
# @OUT cleaned_data  @URI file:{db_pth}/ppp_data_cleaned
def main(db_pth="data"):
    na_values = {"JobsReported": [""]}  # add more columns or values if needed
    df = pd.read_csv(
        f"{db_pth}/ppp_data_after_openrefine.csv", na_values=na_values
    )
    original_df = pd.read_csv(f"{db_pth}/ppp_data.csv", na_values=na_values)

    # @BEGIN remove_nan
    # @IN df  @AS input_data  @URI file:{db_pth}/ppp_data_after_openrefine.csv
    # @OUT df  @AS removed_nan_data
    # Set JobsReported to Int64 to keep NaNs
    df.loc[:, "JobsReported"] = df["JobsReported"].astype("Int64")

    # Replace all 0s in City with NaN
    df.loc[df.City == "0", "City"] = np.nan

    # missed a '_' in OpenRefine so change that to NaN as well
    df.loc[df.City == "_", "City"] = np.nan

    # also missed a "Suite 620"
    df.loc[df.City == "Suite 620", "City"] = np.nan

    # Convert NonProfit to Yes/No boolean type (NonProfit originally only consists of "Y" and "N/A")
    df.loc[:, "NonProfit"] = df["NonProfit"].fillna(False)
    df.loc[:, "NonProfit"] = df["NonProfit"].replace("Y", True)
    df.loc[:, "NonProfit"] = df["NonProfit"].astype(bool)

    # Change the single 'OR-02' value in the CD column to NaN
    df.loc[df.CD == "OR-02", "CD"] = np.nan

    # Drop all rows with NaN
    df = df.dropna()
    # @END remove_nan

    # @BEGIN remove_invalid_cities
    # @IN df  @AS removed_nan_data
    # @OUT df  @AS removed_invalid_cities_data
    # read in cities.csv
    cities = pd.read_csv(f"{db_pth}/cities.csv")

    # create set of valid cities
    valid_cities = cities["name"].to_list()

    # remove all rows with invalid cities
    df_with_invalid_cities = df.copy(deep=True)
    df = df[df["City"].isin(valid_cities)]

    # print differences
    print(
        f"Number of rows with invalid cities: {len(df_with_invalid_cities) - len(df)}"
    )
    # @END remove_invalid_cities

    # @BEGIN type_conversion
    # @IN df  @AS removed_nan_data
    # @OUT df  @AS converted_data
    # convert DateApproved to datetime
    df["DateApproved"] = pd.to_datetime(df["DateApproved"], errors="coerce")

    # convert remaining fields to category
    df["City"] = df["City"].astype("category")
    df["State"] = df["State"].astype("category")
    df["NAICSCode"] = df["NAICSCode"].astype("category")
    df["RaceEthnicity"] = df["RaceEthnicity"].astype("category")
    df["BusinessType"] = df["BusinessType"].astype("category")
    df["Gender"] = df["Gender"].astype("category")
    df["Veteran"] = df["Veteran"].astype("category")
    df["Lender"] = df["Lender"].astype("category")
    df["CD"] = df["CD"].astype("category")
    # @END type_conversion

    # @BEGIN export_cleaned_data
    # @PARAM db_pth
    # @IN df  @AS converted_data
    # @OUT df  @AS cleaned_data  @URI file:{db_pth}/ppp_data_cleaned
    df.to_csv(f"{db_pth}/ppp_data_cleaned.csv", index=False)
    # @END export_cleaned_data


# @END main

if __name__ == "__main__":
    main()
