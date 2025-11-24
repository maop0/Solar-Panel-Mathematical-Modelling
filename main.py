import dual_axis
import fixed_panel
import single_axis
import matplotlib.pyplot as plt

import numpy as np
dual_axis = dual_axis.dual_solar_Energy_calc(0,0,0.2,'1h')
print('dual')
print((dual_axis.iloc[np.where(dual_axis['ac_power'] > 0)])['ac_power'])
single_axis = single_axis.single_solar_Energy_calc(0,0,0.2,'1h')
print('single')
print((single_axis.iloc[np.where(single_axis['ac_power'] > 0)])['ac_power'])
fixed_panel = fixed_panel.fixed_solar_Energy_calc(0,0,0.2,'1h')
print('fixed')
print((fixed_panel.iloc[np.where(fixed_panel['ac_power'] > 0)])['ac_power'])