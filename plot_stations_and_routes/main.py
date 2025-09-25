from functions import open_file, get_stations, plot_map

sheets = [
    "stations_500_capacity_25", 
    "stations_625_capacity_25", 
    "stations_750_capacity_25", 
    "stations_875_capacity_25", 
    "stations_1000_capacity_25"
]

xlsx_path = "./input/Stations_Database.xlsx"
lat_col = "lat rounded"
lon_col = "long rounded"
name_col="station name"
shp_path = "./input/Chicago-San Francisco2.shp"
out_path = "./output/"
rename_map = {
    "station name": "name",
    "lat rounded": "latitude",
    "long rounded": "longitude"
}

xls = open_file(xlsx_path)

# for sheet_name in [sheets[1]]:
for sheet_name in sheets:
    df_stations = get_stations(xls, sheet_name, lat_col, lon_col, name_col, rename_map)
    plot_map(df_stations, shp_path, f"{out_path}/{sheet_name}")