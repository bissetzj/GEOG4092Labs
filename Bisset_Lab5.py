import numpy as np
from lab5functions import slopeAspect, reclassAspect, reclassByHisto
import rasterio
import glob
import pandas as pd

PATH = "./Lab5/data" # path to data folder

DEM = rasterio.open(f"{PATH}/bigElk_dem.tif")
dem_arr = DEM.read(1)
cell_size = DEM.transform[0]

slope, aspect = slopeAspect(dem_arr, cell_size)

re_aspect = reclassAspect(aspect)
re_slope = reclassByHisto(slope, 10)

years = glob.glob(f"{PATH}/L5_big_elk/*.tif")

fire_per = rasterio.open(f"{PATH}/fire_perimeter.tif").read(1)

RRs = []
for i in range(0,20,2):
    B3 = rasterio.open(years[i]).read(1)
    B4 = rasterio.open(years[i+1]).read(1)
    NDVI = (B4-B3)/(B4+B3)
    mean_healthy = np.mean(NDVI[fire_per==2])
    RR = NDVI/mean_healthy
    year = years[i][-11:-7]
    print(f"The mean RR of the burned area for {year} is: {np.mean(RR[fire_per==1])}")
    RRs.append(RR)

CoR = np.zeros_like(RRs[0])
for i in range(RRs[0].shape[0]):
    for j in range(RRs[0].shape[1]):
        xs = list(range(10))
        ys = [x[i][j] for x in RRs]
        slope, intercept = np.polyfit(xs, ys, 1)
        CoR[i][j] = slope

mean_CoR = np.mean(CoR[fire_per==1])
print("The mean coefficient of recovery for the burned area across all years is:", mean_CoR)


def zonal_stats_tab(zone_arr, value_arr, csv_name):
    """
    Creates a dataframe of the mean,std,min,max,count for each zone in the value array,
    and creats a csv file from the dataframe.

    zone_arr = numpy array containing the zones/classes
    value_arr = numpy array containing values
    csv_name = string which will become name of csv file
    """
    value_arr[fire_per != 1] = np.nan # exclude pixels outside of perimeter
    zones = np.unique(zone_arr)
    data = []
    for zone in zones:
        mean = np.nanmean(value_arr[zone_arr == zone])
        std = np.nanstd(value_arr[zone_arr == zone])
        min = np.nanmin(value_arr[zone_arr == zone])
        max = np.nanmax(value_arr[zone_arr == zone])
        count = np.sum(~np.isnan(value_arr[zone_arr == zone]))
        data.append([zone, mean, std, min, max, count])
    df = pd.DataFrame(data, columns=['Zone', 'Mean', 'Standard_Deviation', 'Min', 'Max', 'Count'])
    df.to_csv(csv_name)
    return df

aspect_df = zonal_stats_tab(re_aspect, CoR, "Aspect_classes.csv")
slope_df = zonal_stats_tab(re_slope, CoR, "Slope_classes.csv")

with rasterio.open(f"{PATH}/bigElk_dem.tif") as raster:
    ras_data = raster.read()
    ras_meta = raster.profile

CoR[fire_per != 1] = -99

with rasterio.open("CoR_Raster.tif", 'w', **ras_meta) as dst:
    dst.write(CoR, 1)

print("Since the mean coefficient of recovery across all the years is positive,",
 "we know the vegetation somewhat recovered over time.",
"The aspect classes 4, 5, and 6 (SE, S, SW) have the lowest mean CoRs and the smallest standard deviations.",
"It seems that a south facing aspect is correlated with not as much vegetation recovered.",
"For the slope classes, there doesn't seem to be any strong patterns.",
"The majority of the slopes are in class 0, but the mean and standard deviation aren't drastically different from other classes.")