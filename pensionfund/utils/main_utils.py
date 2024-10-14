import os
import logging
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from typing import Tuple, List, Dict, Any
from utils.dataloader import DataLoader
from utils.pricer import Pricer
from utils.bond import Bond
from utils.hedging import Hedging
from utils.funding_ratio_analysis import FundingRatioAnalysis
from utils.plotting import Plotting


def configure_logging() -> None:
    """
    Configures the logging settings for the pension fund project.

    Creates a log file in the 'logs' directory relative to the project root.
    Sets the log level to INFO and formats the log messages.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_file = os.path.join(project_root, "logs", "pensionfund.log")

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create a file handler with the desired file mode (overwrite in this case)
    file_handler = logging.FileHandler(log_file, mode="w")

    # Set the log level and format for the file handler
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Get the root logger and configure it
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logging.info("Logging is configured for pensionfund")


def load_and_process_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, float]:
    """
    Loads and processes the necessary data for the financial analysis.

    Reads liabilities, hedge analysis, and bond data from an Excel file.

    Returns:
        Tuple containing:
            - df_liabilities (pd.DataFrame): DataFrame of liabilities.
            - df_hedge (pd.DataFrame): DataFrame of hedge analysis.
            - df_bonds (pd.DataFrame): DataFrame of bonds.
            - interest_rate (float): Flat interest rate used in analysis.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(project_root, "data", "data_cardano.xlsx")

    data_loader = DataLoader(file_path)

    df_liabilities, interest_rate = data_loader.read_liabilities()
    df_hedge = data_loader.read_hedge_analysis()
    df_bonds = data_loader.read_bonds()

    logging.info("Data loaded successfully")
    return df_liabilities, df_hedge, df_bonds, interest_rate


def process_liabilities(
    df_liabilities: pd.DataFrame, flat_interest_rate: float
) -> Tuple[Pricer, float, float, float]:
    """
    Processes the liabilities data to compute present value, DV01, and modified duration.

    Args:
        df_liabilities (pd.DataFrame): DataFrame containing liabilities information.
        flat_interest_rate (float): The flat interest rate applied to liabilities.

    Returns:
        Tuple containing:
            - liabilities_pricer (Pricer): Pricer instance for liabilities.
            - pv_liabilities (float): Present value of liabilities.
            - dv01_liabilities (float): DV01 of liabilities.
            - mod_duration_liabilities (float): Modified duration of liabilities.
    """
    times = df_liabilities["year"].values
    cash_flows = df_liabilities["cash_flows"].values

    liabilities_pricer = Pricer(cash_flows, times, flat_interest_rate)
    pv_liabilities = liabilities_pricer.present_value()
    dv01_liabilities = liabilities_pricer.dv01()
    mod_duration_liabilities = liabilities_pricer.modified_duration()

    logging.info(
        f"Liabilities processed: PV={pv_liabilities:,.2f}, DV01={dv01_liabilities:.2f}, ModDuration={mod_duration_liabilities:.4f}"
    )
    return (
        liabilities_pricer,
        pv_liabilities,
        dv01_liabilities,
        mod_duration_liabilities,
    )


def analyze_bonds(df_bonds: pd.DataFrame, flat_interest_rate: float) -> pd.DataFrame:
    """
    Analyzes bond data to compute price, DV01, and modified duration for each bond.

    Args:
        df_bonds (pd.DataFrame): DataFrame containing bond information.
        flat_interest_rate (float): The flat interest rate applied to bonds.

    Returns:
        pd.DataFrame: DataFrame containing metrics for each bond.
    """
    bond_metrics: List[Dict[str, Any]] = []
    for _, row in df_bonds.iterrows():
        bond = Bond(
            name=row["bond_name"],
            coupon=row["coupon"],
            maturity=row["maturity"],
            interest_rate=flat_interest_rate,
            face_value=row.get("face_value", 1),
        )

        bond_times = np.arange(1, bond.maturity + 1)
        bond_pricer = Pricer(
            cash_flows=bond.cash_flows,
            times=bond_times,
            interest_rate=flat_interest_rate,
        )

        price = bond_pricer.present_value()
        dv01 = bond_pricer.dv01()
        modified_duration = bond_pricer.modified_duration()

        bond_metrics.append(
            {
                "Bond Name": bond.name,
                "Coupon": bond.coupon,
                "Maturity": bond.maturity,
                "Price": f"{price:,.4f}",
                "DV01": f"{dv01:,.4f}",
                "Modified Duration": f"{modified_duration:.4f}",
            }
        )

    df_bond_metrics = pd.DataFrame(bond_metrics)
    logging.info(f"Bond analysis completed for {len(bond_metrics)} bonds")
    return df_bond_metrics


def perform_hedging_analysis(
    df_bond_metrics: pd.DataFrame,
    dv01_liabilities: float,
    df_hedge: pd.DataFrame,
    df_bonds: pd.DataFrame,
    flat_interest_rate: float,
    liabilities_pricer: Pricer,
) -> List[Dict[str, Any]]:
    """
    Performs hedging analysis for each bond based on liability DV01 and bond DV01.

    Args:
        df_bond_metrics (pd.DataFrame): DataFrame containing bond metrics.
        dv01_liabilities (float): DV01 of liabilities.
        df_hedge (pd.DataFrame): DataFrame containing hedge analysis data.
        df_bonds (pd.DataFrame): DataFrame containing bond information.
        flat_interest_rate (float): The flat interest rate applied.

    Returns:
        List[Dict[str, Any]]: List of hedging results for each bond.
    """
    hedge_percentage = 0.5
    all_hedging_results: List[Dict[str, Any]] = []

    for _, bond_row in df_bond_metrics.iterrows():
        bond_name = bond_row["Bond Name"]
        bond_dv01_str: str = bond_row["DV01"]
        bond_dv01 = float(bond_dv01_str.replace(",", ""))

        # Create a unique Hedging instance for each bond
        hedging = Hedging(
            liability_dv01=dv01_liabilities,
            bond_dv01=bond_dv01,
            hedge_percentage=hedge_percentage,
        )
        notional = hedging.calculate_notional()

        # Pass bond-specific data to calculate_hedge_ratio_over_time
        bond_details = df_bonds[df_bonds["bond_name"] == bond_name].iloc[0]
        hedge_ratio_over_time = calculate_hedge_ratio_over_time(
            bond_name,
            notional,
            df_hedge,
            bond_details,
            flat_interest_rate,
            hedging,
            liabilities_pricer,
        )

        all_hedging_results.append(
            {
                "bond_name": bond_name,
                "notional": notional,
                "hedge_ratio_over_time": pd.DataFrame(hedge_ratio_over_time),
            }
        )

        logging.info(
            f"Hedging analysis completed for {bond_name} with maturity {bond_details['maturity']} years and coupon {bond_details['coupon']}"
        )
        logging.info(
            f"Optimal notional: {notional:.2f} for {hedge_percentage * 100}% hedge ratio"
        )
    return all_hedging_results


def calculate_hedge_ratio_over_time(
    bond_name: str,
    notional: float,
    df_hedge: pd.DataFrame,
    bond_details: pd.Series,
    flat_interest_rate: float,
    hedging: Hedging,
    liabilities_pricer: Pricer,
) -> List[Dict[str, Any]]:
    """
    Calculates the hedge ratio over time for a specific bond under varying interest rates.

    Args:
        bond_name (str): Name of the bond.
        notional (float): Notional amount for hedging.
        df_hedge (pd.DataFrame): DataFrame containing hedge analysis data.
        bond_details (pd.Series): Series containing details of the bond.
        flat_interest_rate (float): The flat interest rate applied.
        hedging (Hedging): Hedging instance for calculations.

    Returns:
        List[Dict[str, Any]]: List of hedge ratios over time.
    """
    hedge_ratio_over_time: List[Dict[str, Any]] = []
    bond = Bond(
        name=bond_name,
        coupon=bond_details["coupon"],
        maturity=bond_details["maturity"],
        interest_rate=flat_interest_rate,
        face_value=bond_details.get("face_value", 1),
    )

    for _, row in df_hedge.iterrows():
        current_interest_rate = row["interest_rate"]
        bond.interest_rate = current_interest_rate
        bond.cash_flows = bond.generate_cash_flows()

        bond_pricer = Pricer(
            cash_flows=bond.cash_flows,
            times=np.arange(1, bond.maturity + 1),
            interest_rate=current_interest_rate,
        )
        current_bond_dv01 = bond_pricer.dv01()

        # Use the interest_rate parameter instead of modifying the object's state
        current_liability_dv01 = liabilities_pricer.dv01(
            interest_rate=current_interest_rate
        )

        # Calculate current hedge ratio
        current_hedge_ratio = hedging.calculate_hedge_ratio(
            notional, current_liability_dv01, current_bond_dv01
        )

        hedge_ratio_over_time.append(
            {
                "days_from_now": row["days_from_now"],
                "hedge_ratio": current_hedge_ratio,
                "bond_dv01": current_bond_dv01,
                "liability_dv01": current_liability_dv01,
            }
        )

    return hedge_ratio_over_time


def perform_funding_ratio_analysis() -> pd.DataFrame:
    """
    Performs funding ratio analysis to determine the time required to reach full funding.

    Analyzes the impact of additional asset growth rates on the time to achieve full funding.

    Returns:
        pd.DataFrame: DataFrame containing additional rates and corresponding time to full funding.
    """
    funding_analysis = FundingRatioAnalysis(
        initial_funding_ratio=0.8, nominal_rate=0.015
    )
    additional_rates = np.arange(-0.01, 0.051, 0.001)
    time_to_full_funding = funding_analysis.analyze(additional_rates)

    df_time_to_full_funding = pd.DataFrame(
        {
            "additional_rate (%)": list(time_to_full_funding.keys()),
            "time_to_full_funding (years)": list(time_to_full_funding.values()),
        }
    )
    df_time_to_full_funding["time_to_full_funding (years)"] = df_time_to_full_funding[
        "time_to_full_funding (years)"
    ].replace(np.inf, np.nan)

    logging.info("Funding ratio analysis completed")
    return df_time_to_full_funding


def generate_plots(
    pv_liabilities: float,
    df_bond_metrics: pd.DataFrame,
    mod_duration_liabilities: float,
    all_hedging_results: List[Dict[str, Any]],
    df_time_to_full_funding: pd.DataFrame,
) -> None:
    """
    Generates various plots to visualize the financial analysis results.

    Args:
        pv_liabilities (float): Present value of liabilities.
        df_bond_metrics (pd.DataFrame): DataFrame containing bond metrics.
        mod_duration_liabilities (float): Modified duration of liabilities.
        all_hedging_results (List[Dict[str, Any]]): List of hedging results for each bond.
        df_time_to_full_funding (pd.DataFrame): DataFrame containing funding ratio analysis results.
    """
    plotter = Plotting()

    # Preprocess bond metrics
    df_bond_metrics_plot = df_bond_metrics.copy()
    df_bond_metrics_plot["Price"] = (
        df_bond_metrics_plot["Price"].str.replace(",", "").astype(float)
    )
    df_bond_metrics_plot["DV01"] = (
        df_bond_metrics_plot["DV01"].str.replace(",", "").astype(float)
    )
    df_bond_metrics_plot["Modified Duration"] = df_bond_metrics_plot[
        "Modified Duration"
    ].astype(float)

    combined_hedge_ratios = pd.DataFrame()
    combined_dv01_values = pd.DataFrame()

    for result in all_hedging_results:
        bond_name = result["bond_name"]
        df_hedge_ratio = result["hedge_ratio_over_time"]

        # Ensure the necessary columns are present
        expected_columns = {
            "days_from_now",
            "hedge_ratio",
            "bond_dv01",
            "liability_dv01",
        }
        if not expected_columns.issubset(df_hedge_ratio.columns):
            raise ValueError(
                f"DataFrame for bond '{bond_name}' is missing required columns."
            )

        # Prepare data for combined plots
        combined_hedge_ratios[bond_name] = df_hedge_ratio["hedge_ratio"]
        combined_dv01_values[f"{bond_name}_bond_dv01"] = df_hedge_ratio["bond_dv01"]

    # Set the index for the combined dataframes
    days_from_now = all_hedging_results[0]["hedge_ratio_over_time"]["days_from_now"]
    combined_hedge_ratios.index = days_from_now

    # Plot bond metrics comparison
    plotter.plot_bond_metrics_comparison(
        df=df_bond_metrics_plot,
        modified_duration=mod_duration_liabilities,
        filename="bond_metrics_comparison",
    )
    # Plot notional values vs PV of liability
    plotter.plot_notional_vs_liability(
        all_hedging_results=all_hedging_results,
        pv_liability=pv_liabilities,
        filename="notional_vs_liability",
        title="Notional Values of Bonds vs PV of Liability",
        xlabel="Bonds",
        ylabel="Notional Value",
        hue_label="Components",
    )

    # Generate combined hedge ratio plot
    plotter.plot_hedge_ratio(
        df=combined_hedge_ratios,
        filename="combined_hedge_ratios",  # Added file extension for consistency
        title="Combined Hedge Ratios Over Time",
        xlabel="Days from Now",
        ylabel="Hedge Ratio",
    )

    # Plot funding ratio analysis
    plotter.plot_fund(
        df=df_time_to_full_funding,
        x_column="additional_rate (%)",
        y_column="time_to_full_funding (years)",
        name="funding_ratio_analysis",
        title="Expected Time to Full Funding vs. Additional Asset Growth Rate",
        xlabel="Additional Asset Growth Rate (%)",
        ylabel="Time to Full Funding (years)",
    )
