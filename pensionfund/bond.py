import numpy as np
from pricer import Pricer

class Bond:
    def __init__(self, name, coupon, maturity, interest_rate, face_value=1):
        if maturity <= 0:
            raise ValueError("Maturity must be a positive integer.")
        if not (0 <= coupon <= 1):
            raise ValueError("Coupon rate must be between 0 and 1.")
        self.name = name
        self.coupon = coupon
        self.maturity = maturity
        self.interest_rate = interest_rate
        self.face_value = face_value
        self.cash_flows = self.generate_cash_flows()
        self.times = np.arange(1, self.maturity + 1)
        self.pricer = Pricer(self.cash_flows, self.times, self.interest_rate)

    def generate_cash_flows(self):
        """
        Generate annual cash flows for the bond.

        :return: Numpy array of cash flows.
        """
        cash_flows = np.full(self.maturity, self.coupon * self.face_value)
        cash_flows[-1] += self.face_value
        return cash_flows

    def calculate_hedge_ratio(self, liability_dv01, notional):
        """
        Calculate the hedge ratio.

        :param liability_dv01: DV01 of the liabilities.
        :param notional: Notional amount of the bond.
        :return: Hedge ratio.
        """
        bond_dv01 = self.pricer.dv01()
        return (notional * bond_dv01) / liability_dv01
