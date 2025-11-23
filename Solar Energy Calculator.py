import pvlib
import pandas as pd

# 1. 地点
location = pvlib.location.Location(latitude=34, longitude=-118)

# 2. 时间序列
times = pd.date_range('2024-01-01', '2025-01-02', freq='1h', tz='UTC')

# 3. 太阳位置
solpos = location.get_solarposition(times)

# 4. 辐照度模型
poa = pvlib.irradiance.get_total_irradiance(
    surface_tilt=30,              # 倾角
    surface_azimuth=180,          # 朝向
    dni=800,                      # 直射辐照度
    ghi=600,                      # 水平面全球辐照度
    dhi=100,                      # 水平面散射辐照度
    solar_zenith=solpos['apparent_zenith'],   # 太阳天顶角
    solar_azimuth=solpos['azimuth']           # 太阳方位角
)

# 5. 简单组件模型（PVWatts）
pv_power = pvlib.pvsystem.pvwatts_dc(
    poa['poa_global'],  # 板面辐照度
    temp_cell=45,       # 电池温度
    pdc0=350,           # 组件标称功率（W），你可自行调整
    gamma_pdc=-0.003    # 温度系数（1/°C）
)

# convert pv_power to a pandas Series (align with `times`) and save with POA
pv_series = pd.Series(pv_power, index=times, name='pdc')
df = pd.DataFrame({
    'poa_global': poa['poa_global'],
    'pdc': pv_series
})
df.to_csv('solar_output.csv', index_label='time')
