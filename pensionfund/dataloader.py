# data_loader.py
import os
import sys
import pandas as pd

class DataLoader:
    def __init__(self, file_path):
        """
        Initializes the DataLoader with the path to the Excel file.

        Args:
            file_path (str): Path to the Excel file.
        """
        self.file_path = file_path
        self.validate_file()

    def validate_file(self):
        """
        Validates if the Excel file exists.

        Raises:
            SystemExit: If the file does not exist.
        """
        if not os.path.exists(self.file_path):
            print(f"Error: The file '{self.file_path}' does not exist.")
            sys.exit(1)

    def read_liabilities(self):
        """
        Reads and processes the '1. Liabilities' sheet.

        Returns:
            pd.DataFrame: Cleaned liabilities data.
            float: Interest rate.
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name='1. Liabilities', skiprows=1)
            df.columns = ['NaN', 'Year', 'Cash_flows']
            interest_rate_row = df[df['Year'] == 'Interest rate']
            if not interest_rate_row.empty:
                interest_rate = float(interest_rate_row['Cash_flows'].values[0])
                df = df.drop(interest_rate_row.index)
            else:
                print("Error: 'Interest rate' not found in the '1. Liabilities' sheet.")
                sys.exit(1)

            df = df.drop(columns=['NaN']).reset_index(drop=True)
            df = df.dropna(subset=['Year'])
            df = df[df['Year'] != 'Year']
            df.columns = df.columns.str.replace(' ', '_').str.lower()
            df['year'] = df['year'].astype(int)
            df['cash_flows'] = df['cash_flows'].astype(float)
            return df, interest_rate
        except Exception as e:
            print(f"Error reading '1. Liabilities' sheet: {e}")
            sys.exit(1)

    def read_bonds(self):
        """
        Reads and processes the '2. Bonds' sheet.

        Returns:
            pd.DataFrame: Cleaned bonds data.
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name='2. Bonds', skiprows=3)
            df.columns = ['NaN', 'Bond_Name', 'Coupon', 'Maturity', 'NaN_2', 'Cash_flows', 'Price']
            df = df.drop(columns=['NaN', 'NaN_2'])
            df_cleaned = df.dropna(subset=['Bond_Name'])
            df_cleaned = df_cleaned[df_cleaned['Coupon'] != 'Coupon'].reset_index(drop=True)
            df_cleaned.columns = df_cleaned.columns.str.replace(' ', '_').str.lower()
            df_cleaned.rename(columns={'cash_flows': 'cash_flow_bonds'}, inplace=True)
            df_cleaned['coupon'] = df_cleaned['coupon'].astype(float)
            df_cleaned['maturity'] = df_cleaned['maturity'].astype(int)
            df_cleaned['cash_flow_bonds'] = df_cleaned['cash_flow_bonds'].astype(float)
            df_cleaned['price'] = df_cleaned['price'].astype(float)
            return df_cleaned
        except Exception as e:
            print(f"Error reading '2. Bonds' sheet: {e}")
            sys.exit(1)

    def read_hedge_analysis(self):
        """
        Reads and processes the '4. Hedge analysis' sheet.

        Returns:
            pd.DataFrame: Cleaned hedge analysis data.
        """
        try:
            df = pd.read_excel(self.file_path, sheet_name='4. Hedge analysis', skiprows=2)
            df.columns = ['NaN', 'Days_from_now', 'Interest_rate']
            df = df.drop(columns=['NaN'])
            df['Days_from_now'] = range(len(df))
            df.columns = df.columns.str.replace(' ', '_').str.lower()
            df['days_from_now'] = df['days_from_now'].astype(int)
            df['interest_rate'] = df['interest_rate'].astype(float)
            return df
        except Exception as e:
            print(f"Error reading '4. Hedge analysis' sheet: {e}")
            sys.exit(1)
