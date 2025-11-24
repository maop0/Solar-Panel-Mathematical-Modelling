import math
import pandas as pd
from pathlib import Path

# load data
def load_results(csv_path):
    df = pd.read_csv(csv_path, header=None, names=["type", "value"])
    data = df.set_index("type")["value"].to_dict()
    return data
base = Path("outputs")
cq_file = base / "Chongqing_results.csv"
ls_file = base / "Lhasa_results.csv"
ur_file = base / "Urumqi_results.csv"
cq = load_results(cq_file)
ur = load_results(ur_file)
ls = load_results(ls_file)
e_chongqing_fixed = float(cq["fixed_panel"])
e_chongqing_single = float(cq["single_axis"])
e_chongqing_dual = float(cq["dual_axis"])
e_urumqi_fixed = float(ur["fixed_panel"])
e_urumqi_single = float(ur["single_axis"])
e_urumqi_dual = float(ur["dual_axis"])
e_lhasa_fixed = float(ls["fixed_panel"])
e_lhasa_single = float(ls["single_axis"])
e_lhasa_dual = float(ls["dual_axis"])


x1 = 0; x2 = 0
capex = 4841
for t in range(1, 26):
    opex = 120
    x1 += opex / math.pow(1.07, t)
    x2 += e_chongqing_fixed / math.pow(1.07, t)
chongqing_fixed_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 6180
o0 = 60
k = 0.05
for t in range(1, 26):
    opex = 120 + min(o0 * pow(math.e, 24*k), o0 * pow(math.e, k*(t-1)))
    x1 += opex / math.pow(1.07, t)
    x2 += e_chongqing_single / math.pow(1.07, t)
chongqing_single_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 8034
o0 = 150
k = 0.06
for t in range(1, 26):
    opex = 120 + min(o0 * pow(math.e, 24*k), o0 * pow(math.e, k*(t-1)))
    x1 += opex / math.pow(1.07, t)
    x2 += e_chongqing_dual / math.pow(1.07, t)
chongqing_dual_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 4841
for t in range(1, 26):
    opex = 120
    x1 += opex / math.pow(1.07, t)
    x2 += e_urumqi_fixed / math.pow(1.07, t)
urumqi_fixed_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 6180
o0 = 60
k = 0.05
for t in range(1, 26):
    opex = 120 + min(o0 * pow(math.e, 24*k), o0 * pow(math.e, k*(t-1)))
    x1 += opex / math.pow(1.07, t)
    x2 += e_urumqi_single / math.pow(1.07, t)
urumqi_single_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 8034
o0 = 150
k = 0.06
for t in range(1, 26):
    opex = 120 + min(o0 * pow(math.e, 24*k), o0 * pow(math.e, k*(t-1)))
    x1 += opex / math.pow(1.07, t)
    x2 += e_urumqi_dual / math.pow(1.07, t)
urumqi_dual_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 4841
for t in range(1, 26):
    opex = 120
    x1 += opex / math.pow(1.07, t)
    x2 += e_lhasa_fixed / math.pow(1.07, t)
lhasa_fixed_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 6180
o0 = 60
k = 0.05
for t in range(1, 26):
    opex = 120 + min(o0 * pow(math.e, 24*k), o0 * pow(math.e, k*(t-1)))
    x1 += opex / math.pow(1.07, t)
    x2 += e_lhasa_single / math.pow(1.07, t)
lhasa_single_lcoe = (capex + x1) / x2

x1 = 0; x2 = 0
capex = 8034
o0 = 150
k = 0.06
for t in range(1, 26):
    opex = 120 + min(o0 * pow(math.e, 24*k), o0 * pow(math.e, k*(t-1)))
    x1 += opex / math.pow(1.07, t)
    x2 += e_lhasa_dual / math.pow(1.07, t)
lhasa_dual_lcoe = (capex + x1) / x2

print("\n========= LCOE Results =========")
print(f"Chongqing Fixed Panel LCOE (yuan/kWh): {chongqing_fixed_lcoe*1000}")
print(f"Chongqing Single Axis LCOE (yuan/kWh): {chongqing_single_lcoe*1000}")
print(f"Chongqing Dual Axis LCOE (yuan/kWh): {chongqing_dual_lcoe*1000}")
print(f"Urumqi Fixed Panel LCOE (yuan/kWh): {urumqi_fixed_lcoe*1000}")
print(f"Urumqi Single Axis LCOE (yuan/kWh): {urumqi_single_lcoe*1000}")
print(f"Urumqi Dual Axis LCOE (yuan/kWh): {urumqi_dual_lcoe*1000}")
print(f"Lhasa Fixed Panel LCOE (yuan/kWh): {lhasa_fixed_lcoe*1000}")
print(f"Lhasa Single Axis LCOE (yuan/kWh): {lhasa_single_lcoe*1000}")
print(f"Lhasa Dual Axis LCOE (yuan/kWh): {lhasa_dual_lcoe*1000}")