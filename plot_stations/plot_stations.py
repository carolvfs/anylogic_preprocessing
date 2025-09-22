import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from matplotlib.lines import Line2D

def plot(csv_file_path, shapefile_path):

    df = pd.read_csv(csv_file_path)
    latitudes = df["Latitude"]
    longitudes = df["Longitude"]

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

    shp_reader = shapereader.Reader(shapefile_path)
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
    # plt.show()

    png_file_path = f"./stations.pdf"
    fig.savefig(png_file_path, dpi=300, bbox_inches='tight')

if __name__ == '__main__':
    main_path = "./"
    # pushpin = "./pin.png"
    shp_path = "../CHI-SF-ROUTE/Chicago-San Francisco/Chicago-San Francisco2.shp"
    pushpin = "./EV_Station.png"
    csv_file = "./stations.csv"

    plot(csv_file, shp_path)
