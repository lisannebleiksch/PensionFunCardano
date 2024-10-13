# # plotting.py
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# class Plotting:
#     def __init__(self):
#         sns.set(style="whitegrid")

#     def plot_data(self, df, filename, title="Hedge Ratio Over Time", xlabel="Days from Now", ylabel="Hedge Ratio"):
#         """
#         Plot the hedge ratio over time.

#         :param df: Pandas DataFrame containing 'days_from_now' and 'hedge_ratio' columns.
#         :param title: Title of the plot.
#         :param xlabel: Label for the x-axis.
#         :param ylabel: Label for the y-axis.
#         """
#         plt.figure(figsize=(12, 6))
#         sns.lineplot(x='days_from_now', y='hedge_ratio', data=df, marker='o')
#         plt.title(title)
#         plt.xlabel(xlabel)
#         plt.ylabel(ylabel)
#         plt.tight_layout()
#         plt.savefig(f'plots/hedge_ratio_{filename}.png')

#     def plot_fund(self, df, x_column, y_column, name, title="Line Plot", xlabel="X-axis", ylabel="Y-axis"):
#         """
#         Plot a line graph based on the provided DataFrame, add a vertical line at x=0,
#         and display the corresponding y value (interpolated if necessary) rounded to one decimal place.

#         :param df: Pandas DataFrame containing the data.
#         :param x_column: Column name for the x-axis.
#         :param y_column: Column name for the y-axis.
#         :param name: Name of the plot file to save.
#         :param title: Title of the plot.
#         :param xlabel: Label for the x-axis.
#         :param ylabel: Label for the y-axis.
#         """
#         plt.figure(figsize=(12, 6))
        
#         # Ensure the DataFrame is sorted by x_column for interpolation
#         df_sorted = df.sort_values(by=x_column)
        
#         # Plot the line with markers
#         sns.lineplot(x=x_column, y=y_column, data=df_sorted, marker='o')
        
#         # Add vertical line at x=0
#         plt.axvline(x=0, color='red', linestyle='--', linewidth=1)
        
#         # Extract x and y values for interpolation
#         x_values = df_sorted[x_column].values
#         y_values = df_sorted[y_column].values
        
#         # Check if x=0 is within the range of x_values
#         if x_values.min() <= 0 <= x_values.max():
#             # Perform linear interpolation to find y at x=0
#             y_at_zero = np.interp(0, x_values, y_values)
#             y_value_rounded = round(y_at_zero, 1)
            
#             # Annotate the interpolated y value on the plot
#             plt.annotate(
#                 f'y = {y_value_rounded}',
#                 xy=(0, y_at_zero),
#                 xytext=(10, 30),  # Adjusted offset for better visibility
#                 textcoords='offset points',
#                 arrowprops=dict(arrowstyle='->', color='red'),
#                 fontsize=12,
#                 color='red',
#                 backgroundcolor='white'
#             )
#         else:
#             # If x=0 is not within the data range, notify the user
#             plt.text(0, plt.ylim()[1]*0.95, 'y value at x=0 not available',
#                     color='red', ha='left', va='top', fontsize=12)
        
#         # Set plot title and labels
#         plt.title(title)
#         plt.xlabel(xlabel)
#         plt.ylabel(ylabel)
        
#         # Improve layout and save the plot
#         plt.tight_layout()
#         plt.savefig('plots/' + name + '.png')
#         plt.close()  # Close the figure to free memory



# plotting.py
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from bond import Bond

class Plotting:
    def __init__(self):
        sns.set(style="whitegrid")
        # Create the plots directory if it doesn't exist
        if not os.path.exists('plots'):
            os.makedirs('plots')

    def plot_data(self, df, filename, title="Hedge Ratio Over Time", xlabel="Days from Now", ylabel="Hedge Ratio"):
        """
        Plot the hedge ratio over time.
        """
        plt.figure(figsize=(12, 6))
        sns.lineplot(x='days_from_now', y='hedge_ratio', data=df, marker='o')
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.savefig(f'plots/hedge_ratio_{filename}.png')
        plt.close()

    def plot_fund(self, df, x_column, y_column, name, title="Line Plot", xlabel="X-axis", ylabel="Y-axis"):
        """
        Plot a line graph based on the provided DataFrame with additional annotations.
        """
        plt.figure(figsize=(12, 6))
        
        # Ensure the DataFrame is sorted by x_column for interpolation
        df_sorted = df.sort_values(by=x_column)
        
        # Plot the line with markers
        sns.lineplot(x=x_column, y=y_column, data=df_sorted, marker='o')
        
        # Add vertical line at x=0
        plt.axvline(x=0, color='red', linestyle='--', linewidth=1)
        
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
                f'y = {y_value_rounded}',
                xy=(0, y_at_zero),
                xytext=(10, 30),  # Adjusted offset for better visibility
                textcoords='offset points',
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=12,
                color='red',
                backgroundcolor='white'
            )
        else:
            # If x=0 is not within the data range, notify the user
            plt.text(0, plt.ylim()[1]*0.95, 'y value at x=0 not available',
                    color='red', ha='left', va='top', fontsize=12)
        
        # Set plot title and labels
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        
        # Improve layout and save the plot
        plt.tight_layout()
        plt.savefig(f'plots/{name}.png')
        plt.close()

    def plot_bond_metrics_comparison(self, df,modified_duration,filename="bond_metrics_comparison.png"):
        """
        Plot a bar chart comparing Price, DV01, and Modified Duration for each bond.
        """
        # Melt the DataFrame for easier plotting with seaborn
        df_melted = df.melt(id_vars=['Bond Name'], value_vars=['Price', 'Modified Duration'],
                            var_name='Metric', value_name='Value')

        plt.figure(figsize=(14, 7))
        sns.barplot(x='Bond Name', y='Value', hue='Metric', data=df_melted)
        # Add a horizontal line for the modified duration
        plt.axhline(modified_duration,color='red', linestyle='--', label=f'Modified Duration Liability')
    
        plt.title('Comparison of Bond Metrics')
        plt.xlabel('Bond Name')
        plt.ylabel('Value')
        plt.legend(title='Metric')
        plt.tight_layout()
        plt.savefig(f'plots/{filename}')
        plt.close()
