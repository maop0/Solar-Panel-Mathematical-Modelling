import pandas as pd
import pvlib
import numpy as np
from pathlib import Path
import os


def fixed_solar_Energy_calc(surface_tilt, surface_azimuth, para=None,
                      dni=None, dhi=None, ghi=None,
                      albedo=0.2, freq='1h'):
    """
    计算太阳能板输出功率与板面辐照度（POA）
    支持 tilt 随时间变化，支持 DNI/DHI/GHI 自动推算关系。

    参数
    ----
    surface_tilt : float 或 array
        面倾角（度），可为时间序列的 np.array
    surface_azimuth : float
        面朝向（度），北=0° 顺时针
    para : [lat, lon, start_date, end_date]
    dni, dhi, ghi : float 或 array，可选
        如果缺少，会自动推算。
    albedo : float
    freq : str
        时间分辨率
    """

    latitude, longitude, start_date, end_date = para

    # 时间序列
    times = pd.date_range(start=start_date, end=end_date, freq=freq, tz="Asia/Shanghai")

    # 地点对象
    location = pvlib.location.Location(latitude=latitude, longitude=longitude, tz="Asia/Shanghai", altitude=0)

    # 气象数据
    current_dir = os.path.dirname(__file__)
    epw_file_path = os.path.join(current_dir, 'data', 'Chongqing.epw')
    weather_data, meta_data = pvlib.iotools.read_epw(epw_file_path)


    # 太阳位置
    solpos = location.get_solarposition(times)
    solar_zenith = solpos["apparent_zenith"]
    solar_azimuth = solpos["azimuth"]

    # 辐照度输入处理
    N = len(times)

    # Convert scalars to arrays
    arr = lambda x : np.full(N, x) if np.isscalar(x) else np.array(x)

    # Case 1: Only GHI → use Erbs model to get DNI, DHI
    if ghi is not None and dni is None and dhi is None:
        dhi = pvlib.irradiance.erbs(
            ghi, solar_zenith, times
        )["dhi"].values
        dni = pvlib.irradiance.dirint(
            ghi, solar_zenith, times
        )  # W/m2

    # Case 2: Provided DNI and DHI → compute GHI
    if ghi is None and dni is not None and dhi is not None:
        ghi = dhi + dni * np.cos(np.radians(solar_zenith))

    # Case 3: All provided → trust user but convert to array
    if ghi is not None:
        ghi = arr(ghi)

    # 5. surface_tilt 处理（允许时间变化）
    if np.isscalar(surface_tilt):
        tilt = np.full(N, surface_tilt)
    else:
        tilt = np.array(surface_tilt)

    # 6. 计算 POA
    #将NaN转为0
    dni = np.where(np.isnan(dni)==True, 0, dni)
    dhi = np.where(np.isnan(dhi)==True, 0, dhi)
  
   
    poa = pvlib.irradiance.get_total_irradiance(
            surface_tilt=tilt,
            surface_azimuth=surface_azimuth,
            solar_zenith=solar_zenith,
            solar_azimuth=solar_azimuth,
            dni=dni,
            ghi=ghi,
            dhi=dhi,
            albedo=albedo,
        
    )
    # 7. PVWatts 功率模型
    pdc = pvlib.pvsystem.pvwatts_dc(
        poa["poa_global"],
        temp_cell=45,
        pdc0=350,
        gamma_pdc=-0.003
    )

    # 8. 输出 dataframe
    df = pd.DataFrame({
        "solar_zenith": solar_zenith,
        "solar_azimuth": solar_azimuth,
        "dni": dni,
        "dhi": dhi,
        "ghi": ghi,
        "poa_global": poa["poa_global"],
        "pdc": pdc,
        "tilt": tilt,
    }, index=times)

    return df


#
dfs = fixed_solar_Energy_calc (
    surface_tilt=30,
    surface_azimuth=180,
    para=[31.2, 121.5, "2025-05-01", "2025-05-03"],
    ghi=600
)
dfd = single_solar_Energy_calc(axis_tilt=0,axis_azimuth=90,
                               para=[31.2, 121.5, "2025-05-01", "2025-05-03"],
                               ghi=600)
print(dfd)
# Compute hours per time step (robust to single-point series)
if len(df.index) > 1:
    hours_per_period = (df.index[1] - df.index[0]).total_seconds() / 3600.0
else:
    hours_per_period = 1.0

# Energy per period in Wh, then kWh
dfs['energy_Wh'] = df['pdc'] * hours_per_period
dfs['energy_kWh'] = df['energy_Wh'] / 1000.0

# Aggregate to annual totals (year-end frequency). Use 'YE' to avoid FutureWarning.
annual = df['energy_kWh'].resample('YE').sum()
annual.index = annual.index.year
annual_df = annual.to_frame(name='annual_energy_kWh')

"""
# Print and save annual totals (change path if desired)
print(annual_df)

# Determine a portable output directory (script folder if available, otherwise cwd)
try:
    script_dir = Path(__file__).parent
except NameError:
    script_dir = Path.cwd()

output_dir = script_dir / "outputs"
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / "annual_energy.csv"

try:
    annual_df.to_csv(output_path, index=True, encoding="utf-8-sig")
    print(f"Saved annual energy to: {output_path}")
except Exception as e:
    # fallback to user's home directory
    fallback = Path.home() / "annual_energy.csv"
    annual_df.to_csv(fallback, index=True, encoding="utf-8-sig")
    print(f"Failed to save to {output_path!s}, saved to {fallback!s} instead. Error: {e}")
"""