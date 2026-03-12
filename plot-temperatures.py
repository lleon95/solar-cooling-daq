# Copyright 2025 - Instituto Tecnologico de Costa Rica
# Author: Luis G. Leon Vega
# License: See LICENSE

from flirimageextractor import FlirImageExtractor
from sys import argv
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import datetime
import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from dateutil import parser as dateparser
from dotenv import load_dotenv
import pandas as pd
from tqdm import tqdm

load_dotenv()

def configure_meta(temp=25.0, humidity=90.0) -> dict:
    meta = dict()

    meta["Emissivity"] = 0.9
    meta["SubjectDistance"] = "2.6" # Float
    meta["ReflectedApparentTemperature"] = f"{temp} C"
    meta["AtmosphericTemperature"] = f"{temp} C" # Float
    meta["IRWindowTemperature"] = f"{temp} C" # Float
    meta["IRWindowTransmission"] = 1.0
    meta["RelativeHumidity"] = f"{humidity} %" # Float
    meta["PlanckR1"] = 17096.453
    meta["PlanckB"] = 1428
    meta["PlanckF"] = 1
    meta["PlanckO"] = -196
    meta["PlanckR2"] = 0.046588276

    return meta

def get_params(filename: str) -> list:
    datetime_str = os.path.basename(filename).split('_R')[0]  # or just filename[:15]
    local_dt = datetime.datetime.strptime(datetime_str, "%Y%m%d_%H%M%S")

    # Filter by time
    if not (6 <= local_dt.hour < 18):
        return []
    
    # Get params
    if local_dt.month == 9:
        return [110,55,0.88,5.0]
    else:
        if 0 <= local_dt.day <= 7:
            return [110,55,0.88,5.0]
        elif 9 <= local_dt.day <= 13:
            return [110,55,0.95,5.0]
        elif 14 <= local_dt.day <= 15:
            return [110,55,0.8,5.0]
        elif 16 <= local_dt.day <= 19:
            return [98,50,0.8]
        elif local_dt.day == 20:
            return [98,47,0.8]
        else:
            return []




def to_influxdb_time(filename: str) -> str:
    """
    Convert a timestamp string in the format YYYYMMDD_HHMMSS_* 
    (e.g., 20250707_205141_R) to an InfluxDB-compatible RFC3339 timestamp.
    """
    # Extract the date/time part only (ignore trailing parts like "_R")
    # Parse as naive datetime
    datetime_str = os.path.basename(filename).split('_R')[0]  # or just filename[:15]
    local_dt = datetime.datetime.strptime(datetime_str, "%Y%m%d_%H%M%S")

    # Attach UTC−6 timezone
    utc_minus_6 = datetime.timezone(datetime.timedelta(hours=-6))
    local_dt = local_dt.replace(tzinfo=utc_minus_6)

    # Convert to UTC
    utc_dt = local_dt.astimezone(datetime.timezone.utc)

    # Format as RFC3339 (InfluxDB standard)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

def interpolate_at_timestamp(
    url: str,
    token: str,
    org: str,
    bucket: str,
    timestamp_rfc3339: str,
    lookback: datetime.timedelta = datetime.timedelta(minutes=30),
    location: str = "solar_farm",
    system: str = "raspberry_pi",
    measurement: str = "solar_panel_measurement",
    fields=("ambient_humidity", "ambient_temperature"),
):
    """
    Fetch points around the timestamp and linearly interpolate each requested field.
    Returns a dict with the interpolated values at the exact timestamp.
    """
    # Parse the target timestamp (RFC3339) to aware datetime
    t_target = dateparser.isoparse(timestamp_rfc3339)
    t_start = (t_target - lookback).isoformat().replace("+00:00", "Z")
    t_stop  = (t_target + lookback).isoformat().replace("+00:00", "Z")

    fields_filter = " or ".join([f'r["_field"] == "{f}"' for f in fields])

    # Flux: pull both fields, pivot so each row has columns per field, and sort by time
    flux = f"""
from(bucket: "{bucket}")
  |> range(start: {t_start}, stop: {t_stop})
  |> filter(fn: (r) => r["_measurement"] == "{measurement}")
  |> filter(fn: (r) => {fields_filter})
  |> filter(fn: (r) => r["location"] == "{location}")
  |> filter(fn: (r) => r["system"] == "{system}")
  |> keep(columns: ["_time", "_field", "_value"])
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"])
"""

    with InfluxDBClient(url=url, token=token, org=org) as client:
        df = client.query_api().query_data_frame(flux)

    # When multiple tables are returned, query_data_frame can give a list-like object.
    if isinstance(df, list):
        df = pd.concat(df, ignore_index=True) if df else pd.DataFrame()

    # If no data, return None
    if df.empty:
        return {f: None for f in fields}

    # Normalize time column
    # The column is usually named '_time' and already UTC/aware; ensure it's datetime.
    if "_time" in df.columns:
        df["_time"] = pd.to_datetime(df["_time"], utc=True)
        df = df.sort_values("_time").reset_index(drop=True)
    else:
        # sometimes the client returns an index-time dataframe already; fall back
        raise RuntimeError("No _time column returned—cannot interpolate.")

    # Build time series for each field independently and interpolate
    t_target_ns = pd.Timestamp(t_target).value  # ns since epoch for robust comparison

    results = {}
    for field in fields:
        if field not in df.columns:
            results[field] = None
            continue

        series = df[["_time", field]].dropna().copy()
        if series.empty:
            results[field] = None
            continue

        # Exact match?
        exact = series.loc[series["_time"] == pd.Timestamp(t_target)]
        if not exact.empty:
            results[field] = float(exact[field].iloc[0])
            continue

        # Find the two surrounding points
        times_ns = series["_time"].view("int64")  # ns
        vals = series[field].astype(float).to_numpy()

        # indices on either side
        idx_right = times_ns.searchsorted(t_target_ns, side="left")
        idx_left = idx_right - 1

        if idx_left < 0 and idx_right >= len(series):
            # No data at all
            results[field] = None
        elif idx_left < 0:
            # Only a right neighbor -> nearest
            results[field] = float(vals[idx_right])
        elif idx_right >= len(series):
            # Only a left neighbor -> nearest
            results[field] = float(vals[idx_left])
        else:
            # Linear interpolation between left and right
            t0, t1 = float(times_ns.iloc[idx_left]), float(times_ns.iloc[idx_right])
            v0, v1 = float(vals[idx_left]), float(vals[idx_right])
            if t1 == t0:
                # degenerate (same timestamp) -> pick either
                results[field] = v0
            else:
                w = (t_target_ns - t0) / (t1 - t0)
                results[field] = v0 + w * (v1 - v0)

    return results

def post_thermal_data(
    url: str,
    token: str,
    org: str,
    bucket: str,
    timestamp_rfc3339: str,
    thermal_cam_temp_min_left: float,
    thermal_cam_temp_max_left: float,
    thermal_cam_temp_mean_left: float,
    thermal_cam_temp_std_left: float,
    thermal_cam_temp_min_right: float,
    thermal_cam_temp_max_right: float,
    thermal_cam_temp_mean_right: float,
    thermal_cam_temp_std_right: float,
    location: str = "solar_farm",
    system: str = "raspberry_pi",
    measurement: str = "solar_panel_measurement"
):
    """Write thermal camera data to InfluxDB."""

    # Create InfluxDB client
    with InfluxDBClient(url=url, token=token, org=org) as client:
        write_api = client.write_api(write_options=SYNCHRONOUS)

        # You can send a single Point or multiple points in a list
        p = (
            Point(measurement)
            .tag("location", location)
            .tag("system", system)
            .field("thermal_cam_temp_min_left", float(thermal_cam_temp_min_left))
            .field("thermal_cam_temp_max_left", float(thermal_cam_temp_max_left))
            .field("thermal_cam_temp_mean_left", float(thermal_cam_temp_mean_left))
            .field("thermal_cam_temp_std_left", float(thermal_cam_temp_std_left))
            .field("thermal_cam_temp_min_right", float(thermal_cam_temp_min_right))
            .field("thermal_cam_temp_max_right", float(thermal_cam_temp_max_right))
            .field("thermal_cam_temp_mean_right", float(thermal_cam_temp_mean_right))
            .field("thermal_cam_temp_std_right", float(thermal_cam_temp_std_right))
            .time(timestamp_rfc3339, WritePrecision.NS)
        )

        write_api.write(bucket=bucket, org=org, record=p)
        tqdm.write(f"✅ Wrote data for {timestamp_rfc3339}")


def main():
    # Validate arguments
    if len(argv) <= 1:
        print("[ERROR]: needs the image path as an argument.")
        exit(-1)
    
    # Get the folder
    folder = argv[1]
    files = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    print(f"Files to analyse: {len(files)}")
    for filename in tqdm(files, desc="Processing files"):

        timestamp = to_influxdb_time(filename)
        if timestamp is None:
            tqdm.write("Out of the limits")
            continue 

        offset_x = 120
        offset_y = 50
        zoom = 1.0
        zoom2 = 1.0
        '''
        if len(argv) >= 3:
            offset_x = int(argv[2])
        if len(argv) >= 4:
            offset_y = int(argv[3])
        if len(argv) >= 5:
            zoom = float(argv[4])
        if len(argv) >= 6:
            zoom2 = float(argv[5])
        '''
        args = get_params(filename)
        if len(args) == 0:
            tqdm.write("Out of the limits")
            continue 
        if len(args) >= 1:
            offset_x = int(args[0])
        if len(args) >= 2:
            offset_y = int(args[1])
        if len(args) >= 3:
            zoom = float(args[2])
        if len(args) >= 4:
            zoom2 = float(args[3])

        tqdm.write("Reading the data from Influx")
        INFLUX_URL = os.getenv("INFLUX_URL")
        INFLUX_TOKEN = os.getenv("INFLUX_TOKEN")
        INFLUX_ORG = os.getenv("INFLUX_ORG")
        BUCKET = os.getenv("BUCKET")

        out = interpolate_at_timestamp(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG,
            bucket=BUCKET,
            timestamp_rfc3339=timestamp,
            lookback=datetime.timedelta(minutes=90),   # adjust as needed
            location="solar_farm",
            system="raspberry_pi",
            measurement="solar_panel_measurement",
            fields=("ambient_humidity", "ambient_temperature"),
        )
        tqdm.write(f"Humidity: {out['ambient_humidity']}, Temperature: {out['ambient_temperature']} at Timestamp: {timestamp}")
        if out['ambient_temperature'] is None:
            tqdm.write("Cannot read from the DAQ... Skipping")
            continue

        tqdm.write(f"Reading image: {filename} with timestamp: {timestamp}")
        tqdm.write(f"Offset X: {offset_x}, Offset Y: {offset_y}, Zoom: {zoom}, Zoom Outter: {zoom2}")
        
        # Decode image
        flir = FlirImageExtractor()
        meta = configure_meta(temp=out['ambient_temperature'], humidity=out['ambient_humidity'])
        flir.process_image(filename, meta=meta)
        thermal_raw = flir.get_thermal_np()

        tqdm.write("Cropping and warping image")
        

        # Extract the ROIs
        #panel1 = thermal_raw[50:120,106:166]
        #panel2 = thermal_raw[50:120,186:246]
        panel1 = thermal_raw[offset_y:int(offset_y + 70 * zoom2),(offset_x + 0 ):int(offset_x + zoom2 * 60 )]
        panel2 = thermal_raw[offset_y:int(offset_y + 70 * zoom2),(offset_x + 80):int(offset_x + zoom2 * 140)]

        range = [thermal_raw.min(), thermal_raw.max()]
        
        plt.figure(0)
        plt.title("Full Picture")
        plt.imshow(thermal_raw, vmin=range[0], vmax=range[1])
        
        
        # Mapping points - left
        l_src_points = np.array([[10,10],[56,10],[6,62]]).astype(np.float32)
        l_dst_points = np.array([[5,5],[55,5],[5,65]]).astype(np.float32)

        # Mapping points - right
        r_src_points = np.array([[5,10],[48,10],[7,63]]).astype(np.float32)
        r_dst_points = np.array([[5,5],[54,5],[4,65]]).astype(np.float32)
        # Get transformation and warp
        r_warp_mat = cv.getAffineTransform(r_src_points, r_dst_points)
        r_panel = cv.warpAffine(panel2, r_warp_mat, (panel2.shape[1], panel2.shape[0]))
        #r_panel = r_panel[3:42,7:42]
        r_panel_cropped = r_panel[5:int(65 * zoom), 5:int(55 * zoom)]

        l_warp_mat = cv.getAffineTransform(l_src_points, l_dst_points)
        l_panel = cv.warpAffine(panel1, l_warp_mat, (panel1.shape[1], panel1.shape[0]))
        #l_panel = l_panel[3:41,8:43]
        l_panel_cropped = l_panel[5:int(65 * zoom), 5:int(55 * zoom)]
        

        # Plot
        range = [min(r_panel_cropped.min(), l_panel_cropped.min()), max(r_panel_cropped.max(), l_panel_cropped.max())]
        std = (l_panel_cropped.std() + r_panel_cropped.std()) / 2.0
        mean = (l_panel_cropped.mean() + r_panel_cropped.mean()) / 2.0
        tqdm.write(f"Min Temp: {range[0]}, Max Temp: {range[1]}")
        post_thermal_data(
            url=INFLUX_URL,
            token=INFLUX_TOKEN,
            org=INFLUX_ORG,
            bucket=BUCKET,
            timestamp_rfc3339=timestamp,
            thermal_cam_temp_min_left=l_panel_cropped.min(),
            thermal_cam_temp_max_left=l_panel_cropped.max(),
            thermal_cam_temp_mean_left=l_panel_cropped.mean(),
            thermal_cam_temp_std_left=l_panel_cropped.std(),
            thermal_cam_temp_min_right=r_panel_cropped.min(),
            thermal_cam_temp_max_right=r_panel_cropped.max(),
            thermal_cam_temp_mean_right=r_panel_cropped.mean(),
            thermal_cam_temp_std_right=r_panel_cropped.std()
        )
        
        '''
        plt.figure(1)
        plt.title("Left Panel")
        #plt.imshow(l_panel, vmin=range[0], vmax=range[1])
        plt.imshow(l_panel_cropped, vmin=range[0], vmax=range[1])

        plt.figure(2)
        plt.title("Right Panel") 
        plt.imshow(r_panel_cropped, vmin=range[0], vmax=range[1])

        plt.show()
        '''


if __name__ == "__main__":
    main()