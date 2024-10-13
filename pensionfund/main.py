# main.py
import os
import numpy as np
import pandas as pd
from dataloader import DataLoader
from bond import Bond
from pricer import Pricer
from hedging import Hedging
from plotting import Plotting
from funding_ratio_analysis import FundingRatioAnalysis

def main():
    # =========================
    # Loading Data
    # =========================
    # Define the path to the Excel file
    file_path = os.path.join(os.getcwd(), "data", "data_cardano.xlsx")

    # Initialize the DataLoader
    data_loader = DataLoader(file_path)

    # Read and process the Excel sheets
    df_liabilities, interest_rate = data_loader.read_liabilities()
    df_hedge = data_loader.read_hedge_analysis()
    df_bonds = data_loader.read_bonds()

    # Display the first few rows of each DataFrame for verification
    print("\n--- Liabilities Data ---")
    print(df_liabilities.head())

    print("\n--- Hedge Analysis Data ---")
    print(df_hedge.head())

    print("\n--- Bonds Data ---")
    print(df_bonds.head())

    # =========================
    # Process Liabilities
    # =========================

    # Extract times and cash flows from the liabilities DataFrame
    times = df_liabilities['year'].values
    cash_flows = df_liabilities['cash_flows'].values

    # Assume the term structure is flat and take the first interest rate from hedge analysis
    flat_interest_rate = df_hedge['interest_rate'].iloc[0]

    # Create a Pricer object for liabilities
    liabilities_pricer = Pricer(cash_flows, times, flat_interest_rate)

    # Calculate the present value
    pv_liabilities = liabilities_pricer.present_value()
    print(f"\nPresent Value of Liabilities: {pv_liabilities:,.2f}")

    # Calculate DV01
    dv01_liabilities = liabilities_pricer.dv01()
    print(f"DV01 of Liabilities: {dv01_liabilities:,.2f}")

    # Calculate Modified Duration
    mod_duration_liabilities = liabilities_pricer.modified_duration()
    print(f"Modified Duration of Liabilities: {mod_duration_liabilities:.4f}")

    # =========================
    # Process Bonds
    # =========================

    print("\n--- Bonds Analysis ---")
    print(f"Using Flat Interest Rate: {flat_interest_rate*100:.2f}%")

    # Initialize a list to store bond metrics
    bond_metrics = []

    # Iterate over each bond in the DataFrame
    for index, row in df_bonds.iterrows():
        bond_name = row['bond_name']
        coupon = row['coupon']
        maturity = row['maturity']
        face_value = row.get('face_value', 1)  # Assuming face_value column exists, default to 1

        # Instantiate a Bond object
        bond = Bond(name=bond_name, coupon=coupon, maturity=maturity, interest_rate=flat_interest_rate, face_value=face_value)

        # Define the times (years) for the bond
        bond_times = np.arange(1, bond.maturity + 1)

        # Instantiate a Pricer object for the bond
        bond_pricer = Pricer(cash_flows=bond.cash_flows, times=bond_times, interest_rate=flat_interest_rate)

        # Calculate metrics
        price = bond_pricer.present_value()
        dv01 = bond_pricer.dv01()
        modified_duration = bond_pricer.modified_duration()

        # Store the results
        bond_metrics.append({
            'Bond Name': bond_name,
            'Coupon': coupon,
            'Maturity': maturity,
            'Price': price,
            'DV01': dv01,
            'Modified Duration': modified_duration
        })

    # Convert the results to a DataFrame for better display
    df_bond_metrics = pd.DataFrame(bond_metrics)

    # Format the numerical values for readability
    df_bond_metrics['Price'] = df_bond_metrics['Price'].apply(lambda x: f"{x:,.4f}")
    df_bond_metrics['DV01'] = df_bond_metrics['DV01'].apply(lambda x: f"{x:,.4f}")
    df_bond_metrics['Modified Duration'] = df_bond_metrics['Modified Duration'].apply(lambda x: f"{x:.4f}")

    # =========================
    # Plotting Bond Metrics Comparison
    # =========================
    plotter = Plotting()
    
    # For plotting purposes, convert formatted strings back to floats
    df_bond_metrics_plot = df_bond_metrics.copy()
    df_bond_metrics_plot['Price'] = df_bond_metrics_plot['Price'].str.replace(',', '').astype(float)
    df_bond_metrics_plot['DV01'] = df_bond_metrics_plot['DV01'].str.replace(',', '').astype(float)
    df_bond_metrics_plot['Modified Duration'] = df_bond_metrics_plot['Modified Duration'].astype(float)

    # Plot Bond Metrics Comparison
    plotter.plot_bond_metrics_comparison(df_bond_metrics_plot, mod_duration_liabilities, filename="bond_metrics_comparison.png")
    

    # =========================
    # Hedging Analysis
    # =========================

    print("\n--- Hedging Analysis ---")
    hedge_percentage = 0.5  # 50%

    # Select a bond to use for hedging (e.g., bond_a)
    chosen_bond_name = 'bond_c'  # Change this as needed
    chosen_bond_metrics = df_bond_metrics[df_bond_metrics['Bond Name'] == chosen_bond_name]

    if chosen_bond_metrics.empty:
        print(f"No bond found with the name '{chosen_bond_name}'. Please check the bond name.")
        return

    # Extract the bond's DV01
    bond_dv01_str = chosen_bond_metrics['DV01'].values[0]
    bond_dv01 = float(bond_dv01_str.replace(',', ''))

    # Instantiate the Hedging object
    hedging = Hedging(liability_dv01=dv01_liabilities, bond_dv01=bond_dv01, hedge_percentage=hedge_percentage)

    # Calculate the required notional amount
    notional = hedging.calculate_notional()
    print(f"To hedge {int(hedge_percentage * 100)}% of the interest rate risk, you need to purchase {notional:,.2f} notional of {chosen_bond_name}.")

    # =========================
    # Hedge Ratio Over Time
    # =========================

    hedge_ratio_over_time = []

    # Iterate over each row in the first 180 days using 'days_from_now' and 'interest_rate'
    for _, row in df_hedge.iterrows():
        day = row['days_from_now']
        current_interest_rate = row['interest_rate']

        # Update the bond's interest rate
        bond.interest_rate = current_interest_rate

        # Recalculate bond's cash flows and DV01
        bond.cash_flows = bond.generate_cash_flows()
        bond.pricer = Pricer(bond.cash_flows, bond.times, bond.interest_rate)

        # Recalculate bond DV01
        current_bond_dv01 = bond.pricer.dv01()

        # Recalculate liabilities DV01 assuming it changes with interest rates
        # Assuming liabilities are fixed cash flows, but discount rates change
        liabilities_pricer.interest_rate = current_interest_rate
        current_liability_dv01 = liabilities_pricer.dv01()

        # Calculate hedge ratio using the Hedging class
        current_hedge_ratio = hedging.calculate_hedge_ratio(notional, current_liability_dv01, current_bond_dv01)

        # Append to the list
        hedge_ratio_over_time.append({
            'days_from_now': day,
            'hedge_ratio': current_hedge_ratio
        })

    # Convert to DataFrame
    df_hedge_ratio = pd.DataFrame(hedge_ratio_over_time)

    # =========================
    # Plotting the Hedging Ratio Analysis
    # =========================
    # Call the method using the instance
    plotter.plot_data(
        df=df_hedge_ratio,
        filename=chosen_bond_name,
        title="Hedge Ratio of PFFG Over the Next Six Months",
        xlabel="Days from Now",
        ylabel="Hedge Ratio",
    )

    # =========================
    # Funding Ratio Analysis
    # =========================
    # Initialize FundingRatioAnalysis object
    funding_analysis = FundingRatioAnalysis(initial_funding_ratio=0.8, nominal_rate=0.015)

    # Define a range of additional rates (x) for analysis
    # For example, from -1% to +5% in 0.1% increments
    additional_rates = np.arange(-0.01, 0.051, 0.001)  # x from -1% to +5%

    # Analyze and store the expected time to full funding for each x
    time_to_full_funding = funding_analysis.analyze(additional_rates)

    # Convert the results to a DataFrame
    df_time_to_full_funding = pd.DataFrame({
        'additional_rate (%)': list(time_to_full_funding.keys()),
        'time_to_full_funding (years)': list(time_to_full_funding.values())
    })


    # Handle infinite times by setting them to NaN for plotting purposes
    df_time_to_full_funding['time_to_full_funding (years)'] = df_time_to_full_funding['time_to_full_funding (years)'].replace(np.inf, np.nan)

    # =========================
    # Plotting the Funding Ratio Analysis
    # =========================

    plotter.plot_fund(
        df=df_time_to_full_funding,
        x_column='additional_rate (%)',
        y_column='time_to_full_funding (years)',
        name="funding_ratio_analysis",
        title="Expected Time to Full Funding vs. Additional Asset Growth Rate",
        xlabel="Additional Asset Growth Rate (x%)",
        ylabel="Time to Full Funding (years)",
    )
if __name__ == '__main__':
    main()
