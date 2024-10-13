import unittest
import numpy as np
from pensionfund.pricer import Pricer
from pensionfund.bond import Bond
from pensionfund.hedging import Hedging

class TestFinancialModels(unittest.TestCase):
    def test_pricer_present_value(self):
        cash_flows = [100, 100, 1100]
        times = [1, 2, 3]
        interest_rate = 0.05
        pricer = Pricer(cash_flows, times, interest_rate)
        expected_pv = 100 / (1.05)**1 + 100 / (1.05)**2 + 1100 / (1.05)**3
        self.assertAlmostEqual(pricer.present_value(), expected_pv, places=4)

    def test_pricer_dv01(self):
        cash_flows = [100, 100, 1100]
        times = [1, 2, 3]
        interest_rate = 0.05
        pricer = Pricer(cash_flows, times, interest_rate)
        dv01 = pricer.dv01(delta_r=0.0001)
        self.assertTrue(dv01 > 0)

    def test_pricer_modified_duration(self):
        cash_flows = [100, 100, 1100]
        times = [1, 2, 3]
        interest_rate = 0.05
        pricer = Pricer(cash_flows, times, interest_rate)
        mod_duration = pricer.modified_duration(delta_r=0.0001)
        self.assertTrue(mod_duration > 0)

    def test_hedging_notional_calculation(self):
        liability_dv01 = 100000
        bond_dv01 = 0.9163
        hedge_percentage = 0.5
        hedging = Hedging(liability_dv01, bond_dv01, hedge_percentage)
        notional = hedging.calculate_notional()
        expected_notional = (0.5 * 100000) / 0.9163
        self.assertAlmostEqual(notional, expected_notional, places=2)

    def test_hedging_ratio_calculation(self):
        liability_dv01_current = 100000
        bond_dv01_current = 0.9163
        notional = 54589.04
        hedging = Hedging(liability_dv01=100000, bond_dv01=0.9163, hedge_percentage=0.5)
        hedge_ratio = hedging.calculate_hedge_ratio(notional, liability_dv01_current, bond_dv01_current)
        expected_ratio = (54589.04 * 0.9163) / 100000
        self.assertAlmostEqual(hedge_ratio, expected_ratio, places=4)

if __name__ == '__main__':
    unittest.main()
