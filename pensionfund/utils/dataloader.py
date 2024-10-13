import os
import sys
import pandas as pd
from typing import Tuple
import logging


class DataLoader:
    """
    A class to load and process financial data from an Excel file.

    This class provides methods to read and clean data from specific sheets within an Excel file,
    including liabilities, bonds, and hedge analysis data.

    Attributes:
        file_path (str): Path to the Excel file containing the data.
    """

    def __init__(self, file_path: str) -> None:
        """
        Initializes the DataLoader with the path to the Excel file.

        Args:
            file_path (str): Path to the Excel file.

        Raises:
            SystemExit: If the provided file does not exist.
        """
        self.file_path: str = file_path
        self.validate_file()

    def validate_file(self) -> None:
        """
        Validates if the Excel file exists.

        Raises:
            SystemExit: If the file does not exist.
        """
        if not os.path.exists(self.file_path):
            logging.error(f"Error: The file '{self.file_path}' does not exist.")
            sys.exit(1)

    def read_liabilities(self) -> Tuple[pd.DataFrame, float]:
        """
        Reads and processes the '1. Liabilities' sheet from the Excel file.

        The method performs the following steps:
            1. Reads the '1. Liabilities' sheet, skipping the first row.
            2. Renames columns and extracts the interest rate.
            3. Cleans the DataFrame by removing irrelevant rows and columns.
            4. Converts data types to appropriate formats.

        Returns:
            Tuple[pd.DataFrame, float]:
                - Cleaned liabilities data as a DataFrame.
                - Extracted interest rate as a float.

        Raises:
            SystemExit: If 'Interest rate' is not found in the sheet or any other exception occurs during processing.
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name="1. Liabilities", skiprows=1)
            df.columns = ["NaN", "Year", "Cash_flows"]

            # Extract interest rate
            interest_rate_row = df[df["Year"] == "Interest rate"]
            if not interest_rate_row.empty:
                interest_rate = float(interest_rate_row["Cash_flows"].values[0])
                df = df.drop(interest_rate_row.index)
            else:
                logging.error(
                    "Error: 'Interest rate' not found in the '1. Liabilities' sheet."
                )
                sys.exit(1)

            # Clean DataFrame
            df = df.drop(columns=["NaN"]).reset_index(drop=True)
            df = df.dropna(subset=["Year"])
            df = df[df["Year"] != "Year"]
            df.columns = df.columns.str.replace(" ", "_").str.lower()
            df["year"] = df["year"].astype(int)
            df["cash_flows"] = df["cash_flows"].astype(float)

            logging.info("Successfully read and processed '1. Liabilities' sheet.")
            return df, interest_rate
        except Exception as e:
            logging.error(f"Error reading '1. Liabilities' sheet: {e}")
            sys.exit(1)

    def read_bonds(self) -> pd.DataFrame:
        """
        Reads and processes the '2. Bonds' sheet from the Excel file.

        The method performs the following steps:
            1. Reads the '2. Bonds' sheet, skipping the first three rows.
            2. Renames and cleans columns.
            3. Removes irrelevant rows and resets the index.
            4. Converts data types to appropriate formats.

        Returns:
            pd.DataFrame: Cleaned bonds data as a DataFrame.

        Raises:
            SystemExit: If any exception occurs during processing.
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name="2. Bonds", skiprows=3)
            df.columns = [
                "NaN",
                "Bond_Name",
                "Coupon",
                "Maturity",
                "NaN_2",
                "Cash_flows",
                "Price",
            ]
            df = df.drop(columns=["NaN", "NaN_2"])
            df_cleaned = df.dropna(subset=["Bond_Name"])
            df_cleaned = df_cleaned[df_cleaned["Coupon"] != "Coupon"].reset_index(
                drop=True
            )
            df_cleaned.columns = df_cleaned.columns.str.replace(" ", "_").str.lower()
            df_cleaned.rename(columns={"cash_flows": "cash_flow_bonds"}, inplace=True)
            df_cleaned["coupon"] = df_cleaned["coupon"].astype(float)
            df_cleaned["maturity"] = df_cleaned["maturity"].astype(int)
            df_cleaned["cash_flow_bonds"] = df_cleaned["cash_flow_bonds"].astype(float)
            df_cleaned["price"] = df_cleaned["price"].astype(float)

            logging.info("Successfully read and processed '2. Bonds' sheet.")
            return df_cleaned
        except Exception as e:
            logging.error(f"Error reading '2. Bonds' sheet: {e}")
            sys.exit(1)

    def read_hedge_analysis(self) -> pd.DataFrame:
        """
        Reads and processes the '4. Hedge analysis' sheet from the Excel file.

        The method performs the following steps:
            1. Reads the '4. Hedge analysis' sheet, skipping the first two rows.
            2. Renames columns and drops irrelevant columns.
            3. Resets the 'days_from_now' column to ensure continuity.
            4. Converts data types to appropriate formats.

        Returns:
            pd.DataFrame: Cleaned hedge analysis data as a DataFrame.

        Raises:
            SystemExit: If any exception occurs during processing.
        """
        try:
            df = pd.read_excel(
                self.file_path, sheet_name="4. Hedge analysis", skiprows=2
            )
            df.columns = ["NaN", "Days_from_now", "Interest_rate"]
            df = df.drop(columns=["NaN"])

            # Reset 'Days_from_now' to ensure continuity
            df["Days_from_now"] = range(len(df))
            df.columns = df.columns.str.replace(" ", "_").str.lower()
            df["days_from_now"] = df["days_from_now"].astype(int)
            df["interest_rate"] = df["interest_rate"].astype(float)

            logging.info("Successfully read and processed '4. Hedge analysis' sheet.")
            return df
        except Exception as e:
            logging.error(f"Error reading '4. Hedge analysis' sheet: {e}")
            sys.exit(1)
