# plotting.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import pandas as pd
from typing import List, Dict, Any
from utils.bond import Bond
import logging


class Plotting:
    """
    A class to generate and save various financial plots using Matplotlib and Seaborn.

    This class provides methods to plot multiple lines, line graphs with annotations,
    bond metrics comparisons, and notional values versus liabilities. All plots are
    saved to a designated directory within the project structure.

    Attributes:
        plots_dir (str): Path to the directory where plots will be saved.
    """

    def __init__(self) -> None:
        """
        Initializes the Plotting object.

        Sets the Seaborn style and ensures that the plots directory exists within the project root.
        """
        sns.set(style="whitegrid")

        # Determine the project root by navigating one level up from the current file's directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Define the path to the plots directory within the project root
        self.plots_dir: str = os.path.join(project_root, "plots")

        # Create the plots directory if it doesn't exist
        if not os.path.exists(self.plots_dir):
            os.makedirs(self.plots_dir)
            logging.info(f"Created plots directory at: {self.plots_dir}")
        else:
            logging.info(f"Plots directory already exists at: {self.plots_dir}")

    def plot_hedge_ratio(
        self, df: pd.DataFrame, filename: str, title: str, xlabel: str, ylabel: str
    ) -> None:
        """
        Plots multiple lines on a single plot using Matplotlib.

        Each column in the DataFrame represents a separate line to be plotted.

        Args:
            df (pd.DataFrame): DataFrame where each column represents a line to plot.
            filename (str): Name of the file to save the plot image (without extension).
            title (str): Title of the plot.
            xlabel (str): Label for the x-axis.
            ylabel (str): Label for the y-axis.
        """
        plt.figure(figsize=(12, 6))
        for column in df.columns:
            plt.plot(df.index, df[column], label=column, linewidth=3)
        plt.hlines(
            0.5,
            df.index.min(),
            df.index.max(),
            colors="r",
            linestyles="--",
            label="Hedge Ratio = 0.5",
        )
        plt.title(title, fontsize=18)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel, fontsize=14)
        plt.legend(fontsize=16)
        plt.grid(True)
        plt.tight_layout()
        plot_path = os.path.join(self.plots_dir, f"{filename}.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Saved multiple lines plot to: {plot_path}")

    def plot_fund(
        self,
        df: pd.DataFrame,
        x_column: str,
        y_column: str,
        name: str,
        title: str = "Line Plot",
        xlabel: str = "X-axis",
        ylabel: str = "Y-axis",
    ) -> None:
        """
        Plots a line graph based on the provided DataFrame with additional annotations.

        This method plots the specified x and y columns, adds a vertical line at x=0,
        and annotates the interpolated y-value at x=0 if applicable.

        Args:
            df (pd.DataFrame): DataFrame containing the data to plot.
            x_column (str): Name of the column to use for the x-axis.
            y_column (str): Name of the column to use for the y-axis.
            name (str): Name of the file to save the plot image (without extension).
            title (str, optional): Title of the plot. Defaults to "Line Plot".
            xlabel (str, optional): Label for the x-axis. Defaults to "X-axis".
            ylabel (str, optional): Label for the y-axis. Defaults to "Y-axis".
        """
        plt.figure(figsize=(12, 6))

        df_sorted = df.sort_values(by=x_column)

        sns.lineplot(x=x_column, y=y_column, data=df_sorted, marker="o")

        # Add vertical line at x=0
        plt.axvline(x=0, color="red", linestyle="--", linewidth=1)

        # Extract x and y values for interpolation
        x_values = df_sorted[x_column].values
        y_values = df_sorted[y_column].values

        # Check if x=0 is within the range of x_values
        if x_values.min() <= 0 <= x_values.max():
            # Perform linear interpolation to find y at x=0
            y_at_zero = np.interp(0, x_values, y_values)
            y_value_rounded = round(y_at_zero, 1)

            # Annotate the interpolated y value on the plot
            plt.annotate(
                f"y = {y_value_rounded}",
                xy=(0, y_at_zero),
                xytext=(10, 30),
                textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color="red"),
                fontsize=12,
                color="red",
                backgroundcolor="white",
            )
            logging.info(f"Annotated y-value at x=0: {y_value_rounded}")
        else:
            # If x=0 is not within the data range, notify the user
            plt.text(
                0,
                plt.ylim()[1] * 0.95,
                "y value at x=0 not available",
                color="red",
                ha="left",
                va="top",
                fontsize=12,
            )
            logging.warning(
                "x=0 is not within the range of x_values; no annotation added."
            )

        plt.title(title, fontsize=18)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel, fontsize=14)
        plt.tight_layout()
        plot_path = os.path.join(self.plots_dir, f"{name}.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Saved fund plot to: {plot_path}")

    def plot_bond_metrics_comparison(
        self, df: pd.DataFrame, modified_duration: float, filename: str
    ) -> None:
        """
        Plots a bar chart comparing Price and Modified Duration for each bond,
        and adds a horizontal line representing the Modified Duration of liabilities.

        Args:
            df (pd.DataFrame): DataFrame containing bond metrics with columns ['Bond Name', 'Price', 'Modified Duration'].
            modified_duration (float): Modified duration of the liabilities to be represented as a horizontal line.
            filename (str): Name of the file to save the plot image (without extension).
        """
        # Melt the DataFrame for easier plotting with seaborn
        df_melted = df.melt(
            id_vars=["Bond Name"],
            value_vars=["Modified Duration"],
            var_name="Metric",
            value_name="Value",
        )

        plt.figure(figsize=(14, 7))
        sns.barplot(x="Bond Name", y="Value", hue="Metric", data=df_melted)

        # Add a horizontal line for the modified duration
        plt.axhline(
            modified_duration,
            color="red",
            linestyle="--",
            label=f"Modified Duration Liability ({modified_duration:.2f})",
        )

        plt.title("Comparison of Bond Metrics", fontsize=18)
        plt.xlabel("Bond Name", fontsize=14)
        plt.ylabel("Value", fontsize=14)
        plt.legend(title="Metric", fontsize=16)
        plt.tight_layout()
        plot_path = os.path.join(self.plots_dir, f"{filename}.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Saved bond metrics comparison plot to: {plot_path}")

    def plot_notional_vs_liability(
        self,
        all_hedging_results: List[Dict[str, Any]],
        pv_liability: float,
        filename: str = "notional_vs_liability.png",
        title: str = "Notional Values of Bonds vs PV of Liability",
        xlabel: str = "Bonds",
        ylabel: str = "Notional Value",
        hue_label: str = "Components",
    ) -> None:
        """
        Plots the notional values of each bond alongside the Present Value (PV) of liabilities.

        Args:
            all_hedging_results (List[Dict[str, Any]]): List of dictionaries containing 'bond_name', 'notional', and 'hedge_ratio_over_time'.
            pv_liability (float): Present Value of the liability.
            filename (str, optional): Filename to save the plot (default: 'notional_vs_liability.png').
            title (str, optional): Title of the plot.
            xlabel (str, optional): Label for the x-axis.
            ylabel (str, optional): Label for the y-axis.
            hue_label (str, optional): Label for the legend distinguishing bonds and liability.
        """

        bond_names = [result["bond_name"] for result in all_hedging_results]
        notionals = [result["notional"] for result in all_hedging_results]

        df_notional = pd.DataFrame(
            {"Bond Name": bond_names, "Notional Value": notionals}
        )

        plt.figure(figsize=(12, 6))

        # Plot notional values as bars
        sns.barplot(
            x="Bond Name",
            y="Notional Value",
            data=df_notional,
            label="Bond Notional Value (€)",
        )

        # Add a horizontal line for the PV of the liability
        plt.axhline(
            y=pv_liability,
            color="red",
            linestyle="--",
            linewidth=2,
            label=f"PV of Liability ({pv_liability:,.0f})",
        )

        for index, row in df_notional.iterrows():
            plt.text(
                index,
                row["Notional Value"],
                f"{row['Notional Value']:,.0f}",
                color="black",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        plt.title(title, fontsize=18)
        plt.xlabel(xlabel, fontsize=14)
        plt.ylabel(ylabel + " (€)", fontsize=14)

        plt.legend(fontsize=16)

        plt.tight_layout()
        plot_path = os.path.join(self.plots_dir, f"{filename}.png")
        plt.savefig(plot_path)
        plt.close()
        logging.info(f"Saved notional vs liability plot to: {plot_path}")
