import numpy as np

class FundingRatioAnalysis:
    def __init__(self, initial_funding_ratio=0.8, nominal_rate=0.015):
        """
        Initialize the FundingRatioAnalysis object.

        :param initial_funding_ratio: Current funding ratio (Assets / Liabilities).
        :param nominal_rate: Nominal interest rate (liabilities growth rate).
        """
        if not (0 < initial_funding_ratio < 1):
            raise ValueError("Initial funding ratio must be between 0 and 1.")
        if nominal_rate <= 0:
            raise ValueError("Nominal rate must be a positive number.")

        self.initial_funding_ratio = initial_funding_ratio
        self.nominal_rate = nominal_rate

    def time_to_full_funding(self, x):
        """
        Calculate the time to full funding based on additional asset growth rate.

        :param x: Additional rate over nominal (e.g., 0.005 for 0.5%).
        :return: Time to full funding in years. Returns np.inf if funding is unattainable.
        """
        denominator = 1 + self.nominal_rate + x

        # Prevent division by zero or negative rates
        if denominator <= 1:
            return np.inf

        # Calculate time using the simplified formula
        try:
            t = np.log(1.0 / self.initial_funding_ratio) / np.log(denominator)
            return t
        except:
            return np.inf

    def analyze(self, x_values):
        """
        Analyze the time to full funding over a range of additional rates.

        :param x_values: Iterable of additional rates over nominal (e.g., [0.005, 0.01, ...]).
        :return: Dictionary with x_values as keys and times to full funding as values.
        """
        results = {}
        for x in x_values:
            t = self.time_to_full_funding(x)
            results[x] = t
        return results
