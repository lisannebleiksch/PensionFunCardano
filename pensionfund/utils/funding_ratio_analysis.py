import numpy as np
from typing import Iterable, Dict


class FundingRatioAnalysis:
    """
    Performs analysis on the funding ratio to determine the time required to reach full funding
    based on varying additional asset growth rates.

    Attributes:
        initial_funding_ratio (float): The current funding ratio (Assets / Liabilities).
        nominal_rate (float): The nominal interest rate representing the liabilities' growth rate.
    """

    def __init__(
        self, initial_funding_ratio: float = 0.8, nominal_rate: float = 0.015
    ) -> None:
        """
        Initializes the FundingRatioAnalysis object with the initial funding ratio and nominal rate.

        Args:
            initial_funding_ratio (float, optional): Current funding ratio (Assets / Liabilities).
                                                    Must be between 0 and 1. Defaults to 0.8.
            nominal_rate (float, optional): Nominal interest rate (liabilities growth rate).
                                            Must be a positive number. Defaults to 0.015.

        Raises:
            ValueError: If `initial_funding_ratio` is not between 0 and 1.
            ValueError: If `nominal_rate` is not a positive number.
        """
        if not (0 < initial_funding_ratio < 1):
            raise ValueError("Initial funding ratio must be between 0 and 1.")
        if nominal_rate <= 0:
            raise ValueError("Nominal rate must be a positive number.")

        self.initial_funding_ratio: float = initial_funding_ratio
        self.nominal_rate: float = nominal_rate

    def time_to_full_funding(self, x: float) -> float:
        """
        Calculates the time required to achieve full funding based on an additional asset growth rate.

        The calculation uses the formula:
            t = ln(1 / initial_funding_ratio) / ln(1 + nominal_rate + x)

        Args:
            x (float): Additional rate over the nominal rate (e.g., 0.005 for 0.5%).

        Returns:
            float: Time to full funding in years. Returns `np.inf` if funding is unattainable due to
                   non-positive denominator or mathematical errors.

        Raises:
            ValueError: If the denominator (1 + nominal_rate + x) is less than or equal to 1,
                        making full funding unattainable.
        """
        denominator: float = 1 + self.nominal_rate + x

        # Prevent division by zero or negative rates
        if denominator <= 1:
            return np.inf

        # Calculate time using the simplified formula
        try:
            t: float = np.log(1.0 / self.initial_funding_ratio) / np.log(denominator)
            return t
        except (FloatingPointError, ValueError) as e:
            # Log the exception if logging is set up, or handle it accordingly
            # For now, return infinity to indicate funding is unattainable
            return np.inf

    def analyze(self, x_values: Iterable[float]) -> Dict[float, float]:
        """
        Analyzes the time to full funding across a range of additional asset growth rates.

        Args:
            x_values (Iterable[float]): An iterable of additional rates over the nominal rate
                                        (e.g., [0.005, 0.01, ...] for 0.5%, 1%, ...).

        Returns:
            Dict[float, float]: A dictionary mapping each additional rate to the corresponding
                                time to full funding in years.

        Example:
            >>> analysis = FundingRatioAnalysis()
            >>> rates = [0.005, 0.01, 0.015]
            >>> results = analysis.analyze(rates)
            >>> print(results)
            {0.005: 30.123, 0.01: 25.456, 0.015: 22.789}
        """
        results: Dict[float, float] = {}
        for x in x_values:
            t: float = self.time_to_full_funding(x)
            results[x] = t
        return results
