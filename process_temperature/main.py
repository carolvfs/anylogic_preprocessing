import os
from datetime import datetime, timedelta
from functions import extract_lat_lon, filter_lat_lon, extract_temperature, save

nc_folder = "./input"
save_as = "xlsx" # csv | xlsx
# save_as = "csv" # csv | xlsx


bottom_left = None
top_right = None

user_points = None

lon_sf, lat_sf = -122.4194, 37.7749  # San Francisco
lon_chi, lat_chi = -87.6298, 41.8781  # Chicago

user_points = [
    (lat_chi, lon_chi),
    (41.7936901, -88.3573122),
    (41.8504750, -88.3289198),
    (41.9640448, -88.7831990),
    (41.7085128, -90.1744292),
    (41.5516885, -90.3152601),
    (41.7249595, -92.8279869),
    (41.6533285, -93.7708741),
    (41.4947419, -94.2229083),
    (41.6233354, -95.5122103),
    (41.2368045, -95.8367922),
    (41.0104753, -96.3167663),
    (40.9135241, -96.7898706),
    (40.7147769, -99.5439385),
    (41.2258411, -100.7648140),
    (41.1406637, -102.3547913),
    (41.1690562, -105.2792140),
    (41.7936901, -106.5284819),
    (41.7369052, -109.0838026),
    (41.5221550, -109.4392307),
    (41.3011913, -110.5481954),
    (41.3678033, -111.0996667),
    (40.7514267, -111.5412517),
    (40.7942758, -114.1331163),
    (41.1395280, -114.6237379),
    (41.0850145, -115.3687559),
    (40.7397623, -116.0229180),
    (40.6307353, -116.9678188),
    (41.1031857, -117.6038097),
    (40.3036542, -118.3488277),
    (39.6131498, -119.2937285),
    (39.5404651, -119.9842330),
    (39.3224110, -120.2386293),
    (39.4132669, -120.6565662),
    (38.7227624, -121.4015842),
    (38.4320237, -121.9467193),
    (37.7960328, -122.4736832),
]

buffer_distance = 15000

if save_as == "csv":
    if user_points:
        output_folder = "./output/temperature_csv_filtered"
    else:
        output_folder = "./output/temperature_csv"
else:
    if user_points:
        output_folder = "./output/temperature_xlsx_filtered"
    else:
        output_folder = "./output/temperature_xlsx"

os.makedirs(output_folder, exist_ok=True)

CST_DAY_START = 7  # 7am CST (12pm UTC)
CST_DAY_END = 18   # 6pm CST (11pm UTC)
CST_NIGHT_START = 19  # 7pm CST (12am UTC next day)
CST_NIGHT_END = 6     # 6am CST (11am UTC)

# Get all NetCDF files
nc_files = sorted([f for f in os.listdir(nc_folder) if f.endswith("single.nc")])

# Extract Lat Lon
first_file = os.path.join(nc_folder, nc_files[0])

latitudes, longitudes = extract_lat_lon(first_file)

latitudes, longitudes, mask, row_min, row_max, col_min, col_max = filter_lat_lon(latitudes, longitudes, bottom_left, top_right, buffer_distance, user_points)

avg_temp_dict = {}

for nc_file in nc_files:
    date_str = nc_file.split("_")[0]
    date_time = datetime.strptime(date_str, "%Y%m%d%H")

    # Convert UTC to CST
    date_time_cst = date_time - timedelta(hours=6)
    current_date_cst = date_time_cst.date()
    current_hour_cst = date_time_cst.hour

    period = None
    
    if CST_DAY_START <= current_hour_cst <= CST_DAY_END:
        period = "daytime"
    
    elif current_hour_cst <= CST_NIGHT_END or current_hour_cst >= CST_NIGHT_START:
        period = "nighttime"

    dict_key = f"{current_date_cst}_{period}"

    if dict_key not in avg_temp_dict:
        avg_temp_dict[dict_key] = []

    temp = extract_temperature(nc_folder, nc_file, bottom_left, top_right, row_min, row_max, col_min, col_max, mask, user_points)

    avg_temp_dict[dict_key].append(temp)

    print(f"Finished {nc_file}")

save(avg_temp_dict, latitudes, longitudes, output_folder, save_as)