import pandas as pd
import pvlib
import numpy as np
from pathlib import Path
import os

def single_solar_Energy_calc(axis_tilt, axis_azimuth, para=None,
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
    arr = lambda x: np.full(N, x) if np.isscalar(x) else np.array(x)

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
    if np.isscalar(axis_tilt):
        tilt = np.full(N, axis_tilt)
    else:
        tilt = np.array(axis_tilt)

    # 6. 计算 POA
    # 将NaN转为0
    dni = np.where(np.isnan(dni) == True, 0, dni)
    dhi = np.where(np.isnan(dhi) == True, 0, dhi)

    tracker = pvlib.tracking.singleaxis(apparent_zenith=solar_zenith,
                                        apparent_azimuth=solar_azimuth,
                                        axis_azimuth=axis_azimuth,
                                        axis_tilt=axis_tilt, max_angle=60,  # mechanical limit
                                        backtrack=True, gcr=0.35
                                        )
    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tracker['surface_tilt'],
        surface_azimuth=tracker['surface_azimuth'],
        solar_zenith=solpos['apparent_zenith'],
        solar_azimuth=solpos['azimuth'],
        dni=dni,
        ghi=ghi,
        dhi=dhi,
        albedo=albedo
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