import dual_axis
import fixed_panel
import single_axis
import matplotlib.pyplot as plt
import scipy.optimize as opt

import numpy as np



#print('testing....')
dualAxis = dual_axis.dual_solar_Energy_calc

singleAxis = single_axis.single_solar_Energy_calc

fixedPanel = fixed_panel.fixed_solar_Energy_calc

PLACE = 'Chongqing.epw'
#PLACE = 'Lhasa.epw'
#PLACE = 'Urumqi.epw'
print("\n======== THIS IS " +  PLACE+" ===========")
fixedPanelSum = lambda x: fixedPanel(surface_tilt=x[0], surface_azimuth=x[1], albedo=0.2, freq='1h',loc = PLACE)['ac_power'].to_numpy().sum()*(-1)
dualAxisSum = lambda : dualAxis(albedo=0.2, freq='1h',loc = PLACE)['ac_power'].to_numpy().sum()*(-1)
singleAxisSum = lambda x: singleAxis(x[0], x[1],albedo=0.2, freq='1h',loc = PLACE)['ac_power'].to_numpy().sum()*(-1)


r = opt.minimize(fixedPanelSum,[0,0])
print("=========Results===========")
print(r)
print(f"The optimum value for fixedPanelSum is {-fixedPanelSum(r.x)}\nwith surface_tilt and surface_azimuth being{r.x}")
print("\nRunning, do not quit...")

sig = opt.minimize(singleAxisSum,[0,0])
print("=========Results===========")
print(sig)

print(f"The optimum value for singleAxisSum is {-singleAxisSum(sig.x)}\nwith the axis_tilt and axis_azimuth being{sig.x}")

print(f"results for dualAxisSum is {-dualAxisSum()}")

#======sort and compare========

# Compute the dual-axis value once (it has no variables)
dual_val = -dualAxisSum()   # dummy input, ignored by the function

results = {
    "fixed_panel": -fixedPanelSum(r.x),
    "single_axis": -singleAxisSum(sig.x),
    "dual_axis": dual_val
}

sorted_results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

print("\n========= Sorted Energy Results (best → worst) =========")
for k, v in sorted_results.items():
    print(f"{k}: {v}")