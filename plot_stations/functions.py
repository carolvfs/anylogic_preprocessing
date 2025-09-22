import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from matplotlib.lines import Line2D


def plot_map(data_path, lat_col, lon_col, shp_path, out_path):

    
    # df = pd.read_csv(data_path)
    # df = pd.read_excel(data_path, sheet_name='Sheet1', engine='openpyxl')
    df = pd.read_excel(data_path, engine='openpyxl')
    latitudes = df[lat_col]
    longitudes = df[lon_col]

    projection = ccrs.PlateCarree()
    
    fig = plt.figure(figsize=(12, 8))
    ax = plt.axes(projection=projection)
    
    # ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())
    ax.set_extent([-125.0, -84.145, 36.5, 45.0], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
    ax.add_feature(cfeature.LAKES, facecolor='lightblue')

    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, edgecolor='gray')

    shp_reader = shapereader.Reader(shp_path)
    geometries = list(shp_reader.geometries())
    
    ax.add_geometries(
        geometries,
        crs=ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='blue',
        linewidth=1.0
    )

    ax.scatter(longitudes, latitudes, color='green', edgecolors='black', marker='o', s=30, 
               transform=ccrs.PlateCarree(), zorder=5)
    
    ev_station_handle = Line2D([], [], marker='o', color='w', label='Electric Vehicle Charging Stations',
                                 markerfacecolor='green', markeredgecolor='black', markersize=8)
    route_handle = Line2D([], [], color='blue', lw=1.0, label='Route Chicago-San Francisco')
    
    plt.legend(handles=[ev_station_handle, route_handle], loc='upper right')
       

    # plt.title(date)
    plt.show()

    # png_file_path = f"./stations.pdf"
    # fig.savefig(out_path, dpi=300, bbox_inches='tight')