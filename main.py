import dual_axis
import fixed_panel
import single_axis
import matplotlib.pyplot as plt
import scipy.optimize as opt
import numpy as np
import pandas as pd
import os
import warnings
import torch

warnings.filterwarnings("ignore")

np.random.seed(42)

dualAxis = dual_axis.dual_solar_Energy_calc
singleAxis = single_axis.single_solar_Energy_calc
fixedPanel = fixed_panel.fixed_solar_Energy_calc

# location
PLACE = 'Chongqing.epw'  #albedo=0.2
#PLACE = 'Lhasa.epw'     #albedo=0.4
#PLACE = 'Urumqi.epw'    #albedo=0.4
print("\n======== THIS IS " + PLACE +" ===========")
if(PLACE=='Chongqing.epw'):
    alb = 0.2
elif(PLACE=='Lhasa.epw' or PLACE=='Urumqi.epw'):
    alb = 0.4
fixedPanelSum = lambda x: fixedPanel(surface_tilt=x[0], surface_azimuth=x[1], albedo=alb, freq='1h',loc = PLACE)['ac_power'].to_numpy().sum()*(-1)
dualAxisSum = lambda : dualAxis(albedo=alb, freq='1h', loc = PLACE)['ac_power'].to_numpy().sum()*(-1)
singleAxisSum = lambda x: singleAxis(x[0], x[1], albedo=alb, freq='1h', loc = PLACE)['ac_power'].to_numpy().sum()*(-1)

def minimize(func, x0, lr=0.01, steps=5000):
    x = torch.tensor(x0, dtype=torch.float32, requires_grad=True)
    optimizer = torch.optim.Adam([x], lr=lr)
    for i in range(steps):
        optimizer.zero_grad()
        x_np = x.detach().cpu().numpy()
        loss = func(x_np)
        loss = torch.tensor(loss, dtype=torch.float32)
        loss.backward()
        optimizer.step()
    return x.detach().numpy()

r = opt.minimize(fixedPanelSum,[0,0])
r1 = minimize(fixedPanelSum,[0,0])
print("=========Results===========")
print(r)
print(f"The optimum value for fixedPanelSum is {-fixedPanelSum(r.x)}\nwith surface_tilt and surface_azimuth being{r.x}")
print("\nRunning, do not quit...")

sig = opt.minimize(singleAxisSum,[0,180])
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

# Save results to CSV
if not os.path.exists("outputs"):
    os.makedirs("outputs")
output_file_path = "outputs/" + PLACE[0:-4] + "_results.csv"
results_df = pd.DataFrame(sorted_results.items(), columns=["Tracking System", "Energy Output (Wh)"])
results_df.to_csv(output_file_path, index=False)
print(f"\nResults have been saved to '{output_file_path}'.")