import pandas as pd
import pvlib
import numpy as np
from pathlib import Path
import os

def single_solar_Energy_calc(axis_tilt, axis_azimuth,
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



    # 时间序列

    # 气象数据
    current_dir = os.path.dirname(__file__)
    epw_file_path = os.path.join(current_dir, 'data', 'Chongqing.epw')
    weather_data, meta_data = pvlib.iotools.read_epw(epw_file_path)

    #times = pd.date_range(start="2022-01-01", end="2022-12-31", freq = '1h', tz="Asia/Shanghai")    # 地点对象

    start_date = pd.to_datetime('2021-01-01').tz_localize('Asia/Shanghai')
    end_date = pd.to_datetime('2021-12-31').tz_localize('Asia/Shanghai')

    N = len(weather_data)  # 按 tracker 的数量分成 N 段

    # 转换为时间戳
    start_ts = start_date.value
    end_ts = end_date.value

    # 切成 N 份 → 需要 N+1 个边界点
    cut_points = np.linspace(start_ts, end_ts, N )

    # 转回日期
    times = pd.to_datetime(cut_points).tz_localize('Asia/Shanghai')
    weather_data['time'] = times
    weather_data.set_index('time', inplace=True)
    location = pvlib.location.Location(latitude=meta_data['latitude'], longitude=meta_data['longitude'], tz="Asia/Shanghai", altitude=meta_data['altitude'])

    # 太阳位置
    solpos = location.get_solarposition(times)
    solar_zenith = solpos["apparent_zenith"]
    solar_azimuth = solpos["azimuth"]

    # 辐照度输入处理
    N = len(times)

    # Convert scalars to arrays
    arr = lambda x: np.full(N, x) if np.isscalar(x) else np.array(x)

    dni = weather_data['dni']
    dhi = weather_data['dhi']
    ghi = weather_data['ghi']
    # 5. surface_tilt 处理（允许时间变化）
    if np.isscalar(axis_tilt):
        tilt = np.full(N, axis_tilt)
    else:
        tilt = np.array(axis_tilt)

    # 6. 计算 POA

    tracker = pvlib.tracking.singleaxis(apparent_zenith=solar_zenith,
                                        apparent_azimuth=solar_azimuth,
                                        axis_azimuth=axis_azimuth,
                                        axis_tilt=axis_tilt, max_angle=60,  # mechanical limit
                                        backtrack=True, gcr=0.35
                                        )
    tracker = tracker.fillna(0)
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
    poa.fillna(0, inplace=True)

    # 7. PVWatts 功率模型
    pdc = pvlib.pvsystem.pvwatts_dc(
        poa["poa_global"],
        temp_cell=45,
        pdc0=350,
        gamma_pdc=-0.003
    )

    # 使用逆变器模型计算交流功率

    ac_power = pvlib.inverter.pvwatts(pdc, 300)

    # 输出 dataframe
    df = pd.DataFrame({
        "solar_zenith": solar_zenith,
        "solar_azimuth": solar_azimuth,
        "dni": dni,
        "dhi": dhi,
        "ghi": ghi,
        "poa_global": poa["poa_global"],
        "dc_power": pdc,
        "ac_power": ac_power,  # 输出逆变器交流功率
        "tilt": tilt,
    }, index=times)


    return df


a = single_solar_Energy_calc(axis_tilt=0, axis_azimuth=0, albedo=0.2, freq='1h')
print(a)

