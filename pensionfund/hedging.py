# hedging.py
class Hedging:
    def __init__(self, liability_dv01, bond_dv01, hedge_percentage=0.5):
        """
        Initialize the Hedging object.

        :param liability_dv01: DV01 of the liabilities.
        :param bond_dv01: DV01 of the bond.
        :param hedge_percentage: Percentage of interest rate risk to hedge (default is 50%).
        """
        if not (0 < hedge_percentage <= 1):
            raise ValueError("Hedge percentage must be between 0 (exclusive) and 1 (inclusive).")
        if bond_dv01 == 0:
            raise ValueError("Bond DV01 cannot be zero.")
        
        self.liability_dv01 = liability_dv01
        self.bond_dv01 = bond_dv01
        self.hedge_percentage = hedge_percentage

    def calculate_notional(self):
        """
        Calculate the notional amount of the bond required to hedge the desired percentage of interest rate risk.

        :return: Notional amount of the bond.
        """
        desired_hedge_dv01 = self.hedge_percentage * self.liability_dv01
        notional = desired_hedge_dv01 / self.bond_dv01
        return notional

    def calculate_hedge_ratio(self, notional, liability_dv01_current, bond_dv01_current):
        """
        Calculate the hedge ratio based on current DV01s.

        :param notional: Notional amount of the bond.
        :param liability_dv01_current: Current DV01 of the liabilities.
        :param bond_dv01_current: Current DV01 of the bond.
        :return: Current hedge ratio.
        """
        if liability_dv01_current == 0:
            raise ValueError("Liability DV01 cannot be zero.")
        return (notional * bond_dv01_current) / liability_dv01_current
