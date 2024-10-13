import numpy as np

class Pricer:
    def __init__(self, cash_flows, times, interest_rate):
        self.cash_flows = np.array(cash_flows)
        self.times = np.array(times)
        self.interest_rate = interest_rate
    
    def present_value(self):
        discount_factors = (1 + self.interest_rate) ** self.times
        return np.sum(self.cash_flows / discount_factors)
    
    def dv01(self, delta_r=0.0001):
        pv_current = self.present_value()
        pv_new = np.sum(self.cash_flows / (1 + self.interest_rate + delta_r) ** self.times)
        return pv_current - pv_new
    
    def modified_duration(self, delta_r=0.0001):
        dv01 = self.dv01(delta_r)
        pv_current = self.present_value()
        return dv01 / (pv_current * delta_r)
