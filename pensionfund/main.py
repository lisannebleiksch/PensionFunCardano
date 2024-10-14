import logging
from utils.main_utils import (
    configure_logging,
    load_and_process_data,
    process_liabilities,
    analyze_bonds,
    perform_hedging_analysis,
    perform_funding_ratio_analysis,
    generate_plots,
)


def main() -> None:
    """
    Main function to execute the financial analysis workflow.

    Steps:
        1. Configure logging.
        2. Load and process data.
        3. Process liabilities.
        4. Analyze bonds.
        5. Perform hedging analysis.
        6. Perform funding ratio analysis.
        7. Generate plots.
    """
    configure_logging()
    logging.info("Starting financial analysis")

    df_liabilities, df_hedge, df_bonds, flat_interest_rate = load_and_process_data()

    liabilities_pricer, pv_liabilities, dv01_liabilities, mod_duration_liabilities = (
        process_liabilities(df_liabilities, flat_interest_rate)
    )

    df_bond_metrics = analyze_bonds(df_bonds, flat_interest_rate)

    all_hedging_results = perform_hedging_analysis(
        df_bond_metrics,
        dv01_liabilities,
        df_hedge,
        df_bonds,
        flat_interest_rate,
        liabilities_pricer,
    )

    df_time_to_full_funding = perform_funding_ratio_analysis()

    generate_plots(
        pv_liabilities,
        df_bond_metrics,
        mod_duration_liabilities,
        all_hedging_results,
        df_time_to_full_funding,
    )

    logging.info("Financial analysis completed successfully")
    print("Financial analysis completed successfully")


if __name__ == "__main__":
    main()
