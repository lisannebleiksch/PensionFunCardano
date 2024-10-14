import numpy as np
from typing import Iterable, Optional


class Pricer:
    """
    A class to price financial instruments based on their cash flows, timing, and interest rates.

    This class provides methods to calculate the present value, DV01 (Dollar Value of 01),
    and modified duration of a series of cash flows.

    Attributes:
        cash_flows (np.ndarray): Array of cash flow amounts.
        times (np.ndarray): Array of time periods corresponding to each cash flow.
        interest_rate (float): The discount interest rate used for pricing.
    """

    def __init__(
        self, cash_flows: Iterable[float], times: Iterable[int], interest_rate: float
    ) -> None:
        """
        Initializes the Pricer with cash flows, their corresponding times, and the interest rate.

        Args:
            cash_flows (Iterable[float]): Iterable containing the cash flow amounts.
            times (Iterable[int]): Iterable containing the time periods (e.g., years) for each cash flow.
            interest_rate (float): The discount interest rate (as a decimal, e.g., 0.05 for 5%).

        Raises:
            ValueError: If the lengths of `cash_flows` and `times` do not match.
            ValueError: If `interest_rate` is negative.
        """
        cash_flows_array = np.array(cash_flows, dtype=float)
        times_array = np.array(times, dtype=int)

        if cash_flows_array.shape[0] != times_array.shape[0]:
            raise ValueError(
                "The number of cash flows must match the number of time periods."
            )
        if interest_rate < 0:
            raise ValueError("Interest rate cannot be negative.")

        self.cash_flows: np.ndarray = cash_flows_array
        self.times: np.ndarray = times_array
        self.interest_rate: float = interest_rate

    def present_value(self, interest_rate: Optional[float] = None) -> float:
        """
        Calculates the present value (PV) of the cash flows based on the interest rate.

        The present value is computed using the discrete formula:
            PV = Σ (Cash Flow_t) / (1 + r)^t
        where:
            - Cash Flow_t is the cash flow at time t.
            - r is the interest rate.
            - t is the time period.

        Returns:
            float: The present value of the cash flows.
        """
        if interest_rate is None:
            interest_rate = (
                self.interest_rate
            )  # Use the stored interest rate if not provided
        discount_factors = 1 / (1 + interest_rate) ** self.times
        pv = np.sum(self.cash_flows * discount_factors)
        return pv

    def dv01(
        self, interest_rate: Optional[float] = None, delta_r: float = 0.0001
    ) -> float:
        """
        Calculates the DV01 (Dollar Value of 01) of the cash flows.

        DV01 measures the change in present value for a 1 basis point (0.01%) change in interest rate.
        It is calculated by using the central difference `delta_r`.

        Args:
            delta_r (float, optional): The small change in interest rate (default is 0.0001, representing 1 basis point).

        Returns:
            float: The DV01 of the cash flows.
        """
        if interest_rate is None:
            interest_rate = (
                self.interest_rate
            )  # Use the stored interest rate if not provided
        pv_up = self.present_value(interest_rate=interest_rate + delta_r)
        pv_down = self.present_value(interest_rate=interest_rate - delta_r)
        dv01 = (pv_down - pv_up) / 2
        return dv01

    def modified_duration(self, delta_r: float = 0.0001) -> float:
        """
        Calculates the modified duration of the cash flows.

        Modified duration measures the sensitivity of the present value to changes in interest rates.
        It is defined as:
            Modified Duration = DV01 / (PV * delta_r)

        Args:
            delta_r (float, optional): The small change in interest rate used in DV01 calculation (default is 0.0001).

        Returns:
            float: The modified duration of the cash flows.

        Raises:
            ValueError: If the present value is zero, leading to division by zero.
        """
        dv01 = self.dv01(delta_r)
        pv_current = self.present_value()

        if pv_current == 0:
            raise ValueError(
                "Present value is zero, cannot calculate modified duration."
            )

        modified_duration = dv01 / (pv_current * delta_r)
        return modified_duration
