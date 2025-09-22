from functions import process_stations_info

# latitude, longitude, name, sheet_name
stations = process_stations_info( 
    file_path = "C:/Users/hh8yvn/OneDrive - James Madison University/Carolina/Papers/BETS_Anylogic/code_support/Stations_Database.xlsx",
    sheets = ["stations_500_capacity_25", "stations_625_capacity_25", "stations_750_capacity_25", "stations_875_capacity_25", "stations_1000_capacity_25"],
    lat_col = "lat rounded",
    lon_col = "long rounded",
    name_col="station name",
    out_path = "C:/Users/hh8yvn/OneDrive - James Madison University/Carolina/Papers/BETS_Anylogic/code_support/Stations_Database_processed.xlsx",
    rename_map = {
        "lat rounded": "latitude",
        "long rounded": "longitude",
        "station name": "name"
    }
)