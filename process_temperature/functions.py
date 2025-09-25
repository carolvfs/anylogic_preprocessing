from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
from shapely.geometry import LineString, Point
from shapely.ops import transform
from shapely.prepared import prep
from pyproj import Transformer

def __convert_longitudes(longitudes):
    return np.where(longitudes > 180, longitudes - 360, longitudes)

def extract_lat_lon(file):
    latitudes, longitudes = None, None
    
    with Dataset(file, mode='r') as dataset:
        latitudes = dataset.variables["latitude"][:]
        longitudes = dataset.variables["longitude"][:]

    longitudes = __convert_longitudes(longitudes)

    print("Lat/Lon extracted")

    return latitudes, longitudes

def extract_temperature(nc_folder, nc_file, bottom_left, top_right, row_min, row_max, col_min, col_max, mask, user_points):
    with Dataset(os.path.join(nc_folder, nc_file), 'r') as ds:
        temp = ds.variables["t"][:]
        temp = np.asarray(np.ma.filled(temp, np.nan), dtype=np.float32)

        if bottom_left and top_right:
            temp = temp[row_min:row_max+1, col_min:col_max+1]
        
        elif user_points:
            temp = temp[mask]
        
        temp = temp - 273.15
        temp = np.round(temp, 0)
        # temp = np.rint(temp)

    return temp

def filter_lat_lon(latitudes, longitudes, bottom_left, top_right, buffer_distance, user_points=None):
    mask = row_min = row_max = col_min = col_max = None

    if bottom_left and top_right:
        row_min, row_max, col_min, col_max = __filter_bbox(latitudes, longitudes, bottom_left, top_right)

        latitudes = latitudes[row_min:row_max+1, col_min:col_max+1]
        longitudes = longitudes[row_min:row_max+1, col_min:col_max+1]

    elif user_points:
        mask = __filter_by_route(latitudes, longitudes, buffer_distance, user_points)

        latitudes = latitudes[mask]
        longitudes = longitudes[mask]

    return latitudes, longitudes, mask, row_min, row_max, col_min, col_max

def __filter_bbox(latitudes, longitudes, bottom_left, top_right):
    lat_min, lat_max = bottom_left[0], top_right[0]
    lon_min, lon_max = bottom_left[1], top_right[1]

    region_mask = (
        (latitudes >= lat_min) & (latitudes <= lat_max) &
        (longitudes >= lon_min) & (longitudes <= lon_max)
    )

    rows, cols = np.where(region_mask)

    if rows.size == 0 or cols.size == 0:
        raise ValueError("BBox selection returned no grid cells; check coordinates.")
    
    return rows.min(), rows.max(), cols.min(), cols.max()

def __filter_by_route(latitudes, longitudes, buffer_distance, user_points=None): # [(lat_sf, lon_sf), (lat_chi, lon_chi)]
    if not user_points:
        raise ValueError("user_points must be provided as a list of (lat, lon) tuples")
    
    latitudes_list, longitudes_list = zip(*user_points)
    points_list = list(zip(longitudes_list, latitudes_list))
    route_wgs84 = LineString(points_list)
    
    # transformer = Transformer.from_crs('epsg:4326', 'esri:102003', always_xy=True)
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:5070", always_xy=True)
    route_proj = transform(transformer.transform, route_wgs84)
    
    # buffer_distance should be in PROJ meters (EPSG:5070 uses meters)
    route_buffer_proj = route_proj.buffer(buffer_distance) # meters
    
    # Project the points
    lat_flat = latitudes.flatten()
    lon_flat = longitudes.flatten()

    x_flat, y_flat = transformer.transform(lon_flat, lat_flat)

    points_proj = [Point(xy) for xy in zip(x_flat, y_flat)]

    prep_route_buffer_proj = prep(route_buffer_proj)

    mask_flat = np.array([prep_route_buffer_proj.contains(point) for point in points_proj])

    mask = mask_flat.reshape(latitudes.shape).astype(bool)

    # print(mask.shape)

    print(f"Mask has {np.sum(mask)} True values out of {mask.size} total points.")

    return mask

def save(avg_temp_dict, latitudes, longitudes, output_folder, save_as):
    unique_latitudes = np.unique(latitudes)
    unique_longitudes = np.unique(longitudes)

    df_lat_lon = pd.DataFrame({
        "latitude": unique_latitudes.flatten(),
        "longitude": unique_longitudes.flatten(),
    })

    if save_as == "csv":
        output_file = os.path.join(output_folder, f"points.csv")
        df_lat_lon.to_csv(output_file, index=False)

    else:
        output_file = os.path.join(output_folder, f"points.xlsx")
        df_lat_lon.to_excel(output_file, index=False, engine='openpyxl')
    
    print(f"Processed points and saved to {output_file}")

    for key, temp_arr in avg_temp_dict.items():
        avg_temp = np.mean(temp_arr, axis=0)

        df = pd.DataFrame({
            "latitude": latitudes.flatten(),
            "longitude": longitudes.flatten(),
            "value": avg_temp.flatten()
        })

        if save_as == "csv":
            output_file = os.path.join(output_folder, f"{key}.csv")
            df.to_csv(output_file, index=False)

        else:
            output_file = os.path.join(output_folder, f"{key}.xlsx")
            df.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Processed {key} and saved to {output_file}")