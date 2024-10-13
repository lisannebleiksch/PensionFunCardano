from typing import Any


class Hedging:
    """
    Represents a hedging strategy to mitigate interest rate risk based on DV01 measures.

    """

    def __init__(
        self, liability_dv01: float, bond_dv01: float, hedge_percentage: float = 0.5
    ) -> None:
        """
        Initializes the Hedging object with liability and bond DV01s and the desired hedge percentage.

        Args:
            liability_dv01 (float): DV01 of the liabilities.
            bond_dv01 (float): DV01 of the bond.
            hedge_percentage (float, optional): Percentage of interest rate risk to hedge.
                                                Must be between 0 (exclusive) and 1 (inclusive).
                                                Defaults to 0.5 (50%).

        Raises:
            ValueError: If `hedge_percentage` is not between 0 (exclusive) and 1 (inclusive).
            ValueError: If `bond_dv01` is zero, which would make hedging impossible.
        """
        if not (0 < hedge_percentage <= 1):
            raise ValueError(
                "Hedge percentage must be between 0 (exclusive) and 1 (inclusive)."
            )
        if bond_dv01 == 0:
            raise ValueError("Bond DV01 cannot be zero.")

        self.liability_dv01: float = liability_dv01
        self.bond_dv01: float = bond_dv01
        self.hedge_percentage: float = hedge_percentage

    def calculate_notional(self) -> float:
        """
        Calculates the notional amount of the bond required to hedge the desired percentage of interest rate risk.

        The notional amount is determined by the formula:
            notional = (hedge_percentage * liability_dv01) / bond_dv01

        Returns:
            float: The calculated notional amount of the bond.

        Raises:
            ZeroDivisionError: If `bond_dv01` is zero, which should not occur due to validation in `__init__`.
        """
        desired_hedge_dv01: float = self.hedge_percentage * self.liability_dv01
        try:
            notional: float = desired_hedge_dv01 / self.bond_dv01
            return notional
        except ZeroDivisionError as e:
            # This should not occur due to validation in __init__, but handled for safety
            raise ZeroDivisionError(
                "Bond DV01 is zero, cannot calculate notional."
            ) from e

    def calculate_hedge_ratio(
        self, notional: float, liability_dv01_current: float, bond_dv01_current: float
    ) -> float:
        """
        Calculates the current hedge ratio based on updated DV01 values.

        The hedge ratio determines the proportion of the bond position needed to hedge against current interest rate changes.

        The hedge ratio is calculated using the formula:
            hedge_ratio = (notional * bond_dv01_current) / liability_dv01_current

        Args:
            notional (float): Notional amount of the bond.
            liability_dv01_current (float): Current DV01 of the liabilities.
            bond_dv01_current (float): Current DV01 of the bond.

        Returns:
            float: The calculated hedge ratio.

        Raises:
            ValueError: If `liability_dv01_current` is zero, as it would lead to division by zero.
        """
        if liability_dv01_current == 0:
            raise ValueError("Liability DV01 cannot be zero.")

        hedge_ratio: float = (notional * bond_dv01_current) / liability_dv01_current
        return hedge_ratio
