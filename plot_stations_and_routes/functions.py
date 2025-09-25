import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io import shapereader
from matplotlib.lines import Line2D
from cartopy.mpl.geoaxes import GeoAxes
from typing import cast, Any
import matplotlib.patches as mpatches
from matplotlib.legend_handler import HandlerTuple
from matplotlib.legend_handler import HandlerBase

import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

class LegendImage:
    pass

class HandlerImage(HandlerBase):
    def __init__(self, img_path, zoom=0.08):
        super().__init__()
        self._img = mpimg.imread(img_path)
        self._zoom = zoom

    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        oi = OffsetImage(self._img, zoom=self._zoom)
        ab = AnnotationBbox(
            oi,
            (xdescent + width/2, ydescent + height/2),
            xycoords=trans, frameon=False, box_alignment=(0.68, 0.55)
        )
        return [ab]

def add_icon_above_points(ax, lons, lats, img_path, zoom=0.06, y_offset_pts=10, zorder=8):
    """
    Add a PNG icon slightly above each (lon, lat) point.
    - zoom: scale for the PNG (tweak per DPI/figure size)
    - y_offset_pts: vertical offset in points above the data point
    """
    img = mpimg.imread(img_path)
    for x, y in zip(lons, lats):
        ab = AnnotationBbox(
            OffsetImage(img, zoom=zoom),
            (x, y),
            xycoords=ax.transData,          # lon/lat in current projection
            boxcoords="offset points",      # offset the icon in points
            xybox=(0, y_offset_pts),        # move icon up a bit
            box_alignment=(0.5, 0.0),       # bottom-center of icon aligns to offset point
            frameon=False,
            pad=0.0,
            zorder=zorder,
            annotation_clip=True            # don't render outside axes
        )
        ax.add_artist(ab)


def add_north_arrow_image(
    ax,
    image_path: str,
    location=(0.95, 0.92),   # (x, y) in axes coords (0–1)
    zoom=0.12,               # size; tweak for your figure
    box_alignment=(0.5, 0.5) # anchor inside the image box
):
    """
    Overlay a north-arrow image (PNG with transparency recommended) on a Cartopy GeoAxes.
    """
    img = mpimg.imread(image_path)  # PNG/JPG; use a transparent PNG for best results
    oi = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(
        oi,
        location,
        xycoords=ax.transAxes,
        frameon=False,
        box_alignment=box_alignment,
        zorder=1000
    )
    ax.add_artist(ab)


def add_scalebar(ax, length_km: int = 200, location=(0.1, 0.05), linewidth=3):
    """
    Add a scale bar to a Cartopy GeoAxes.
    
    Parameters
    ----------
    ax : cartopy.mpl.geoaxes.GeoAxes
        The GeoAxes to draw the scalebar on.
    length_km : int
        Length of the scalebar in kilometers.
    location : tuple
        Location in axis coordinates (0–1, 0–1), e.g. (0.1, 0.05) = 10% from left, 5% from bottom.
    linewidth : int
        Thickness of the scalebar line.
    """
    # Get axis extent in data coordinates
    lon_min, lon_max, lat_min, lat_max = ax.get_extent(ccrs.PlateCarree())
    lon_center = (lon_min + lon_max) / 2

    # Convert km → degrees longitude at map center latitude
    import numpy as np
    km_per_degree = 111.32 * np.cos(np.deg2rad(lat_min + (lat_max - lat_min)/2))
    length_deg = length_km / km_per_degree

    # Bar start position in axis coords → data coords
    x0, y0 = ax.transAxes.transform(location)   # axis coords → display
    lon0, lat0 = ax.transData.inverted().transform((x0, y0))  # display → data

    # Draw scalebar
    ax.plot(
        [lon0, lon0 + length_deg], [lat0, lat0],
        transform=ccrs.PlateCarree(),
        color="black", linewidth=linewidth, solid_capstyle="butt"
    )

    # Add text label
    ax.text(
        lon0 + length_deg/2, lat0 - 0.3, f"{length_km} km",
        transform=ccrs.PlateCarree(),
        ha="center", va="top", fontsize=8
    )


def get_stations(
    xls,
    sheet_name: str,
    lat_col: str,
    lon_col: str,
    name_col: str,
    rename_map: dict | None =None
):
    df = pd.read_excel(xls, sheet_name=sheet_name)
    df['sheet_name'] = sheet_name

    filtered = df[[lat_col, lon_col, name_col, 'sheet_name']]

    if rename_map:
        filtered = filtered.rename(columns=rename_map)

    return filtered  


def open_file(xlsx_path):
    return pd.ExcelFile(xlsx_path)

def plot_map(df, shp_path, out_path):

    projection = ccrs.PlateCarree()

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(1, 1, 1, projection=projection)
    ax = cast(GeoAxes, ax) # helps Pylance recognize Cartopy methods

    # ######## # Extension
    ax.set_extent([-125.0, -76.0, 26, 49.3], crs=ccrs.PlateCarree())

    
    # ######## # Map features
    ax.add_feature(cfeature.LAND, facecolor="#f7f7f7", zorder=0)
    ax.add_feature(cfeature.OCEAN, facecolor='#C3D7F9')
    ax.add_feature(cfeature.LAKES, facecolor='#C3D7F9')
    ax.add_feature(
        cfeature.STATES, 
        edgecolor="#bcbcbc", linewidth=0.4, linestyle="-", facecolor="none",
        zorder=1, alpha=0.4
    )

    
    # ######## # Route
    shp_reader = shapereader.Reader(shp_path)
    geometries = list(shp_reader.geometries())
    
    ax.add_geometries(
        geometries,
        crs=ccrs.PlateCarree(),
        facecolor='none',
        edgecolor='black',
        linewidth=0.5
    )

    
    # ######## # Artificial stations
    mask_artificial = df["name"].str.contains("Artificial", case=False, na=False)
    n_artificial = mask_artificial.sum()
    
    ax.scatter(
        df.loc[mask_artificial, "longitude"],
        df.loc[mask_artificial, "latitude"],
        transform=ccrs.PlateCarree(),
        s=30,
        marker="o",
        color="#D55E00",
        linewidth=0,
        edgecolors="none",
        zorder=6,
        label="Artificial Stations",
    )

    if mask_artificial.any():
        add_icon_above_points(
            ax,
            df.loc[mask_artificial, "longitude"].values,
            df.loc[mask_artificial, "latitude"].values,
            img_path="./input/flag.png",
            zoom=0.03,
            y_offset_pts=0,
            zorder=8
        )

    # ######## # Real stations
    n_real = (~mask_artificial).sum()

    ax.scatter(
        df.loc[~mask_artificial, "longitude"],
        df.loc[~mask_artificial, "latitude"],
        transform=ccrs.PlateCarree(),
        s=30,
        marker="o",
        color="#666666",
        edgecolors="none",
        linewidth=0,
        zorder=5,
        label="Other Stations",
    )
    
    handles: list[Any] = [
        Line2D([], [], color='black', lw=1.0, label='Routes'),
        Line2D([], [], marker="o", color="w", markerfacecolor="#666666",
            markeredgecolor="none", markersize=6, label=f"Real EV Charging Stations (total of {n_real})"),
    ]

    labels: list[str] = [h.get_label() for h in handles]
    
    if mask_artificial.any():
        flag_handle = LegendImage()
        handles.append(flag_handle)
        labels.append(f"Artificial EV Charging Stations (total of {n_artificial})")

    ax.legend(
        handles, labels,
        handler_map={LegendImage: HandlerImage("./input/flag.png", zoom=0.025)},
        loc="upper right", fontsize=8, frameon=True, markerscale=0.9, labelspacing=0.8
    )
    
       
    add_scalebar(ax, length_km=200, location=(0.1, 0.05))
    add_north_arrow_image(ax, "./input/north_arrow.png", location=(0.05, 0.06), zoom=0.035)
    # plt.show()
    fig.savefig(out_path, dpi=300, bbox_inches='tight')
    plt.close(fig)


