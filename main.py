import dual_axis
import numpy as np
dual_axis = dual_axis.dual_solar_Energy_calc(0,0,0.2,'1h')
print(dual_axis.iloc[np.where(dual_axis > 0)])