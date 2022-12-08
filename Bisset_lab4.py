import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import glob
from moving_window import mean_filter
from scipy.spatial import distance

PATH = "./data/data/*.tif"  # path to tif files
PATH2 = "./data/data/transmission_stations.txt" # path to text file of transmission stations

def raster_reproject(raster_file):
    dst_crs = 'ESRI:102028'
    src = raster_file
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height
    })    
    dst = np.zeros((1765, 1121), np.uint8)
    for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination = dst,
                src_transform=src.transform,
                src_crs=src.crs,
                dst_transform=transform,
                dst_crs=dst_crs,
                resampling=Resampling.nearest)
    return dst

PA = []
S = []
UA = []
WB = []
WS = []

for f in glob.glob(PATH):
    with rasterio.open(f) as raster_obj:
        raster_obj = raster_reproject(raster_obj)
        mask = np.ones((11,9))
        mean_array = mean_filter(raster_obj, mask)
        print(f, "Done with moving window")
        if "protected_areas" in f:
            PA = 1*(mean_array < 0.05)
        elif "slope" in f:
            S = 1*(mean_array < 15)
        elif "urban_areas" in f:
            UA = 1*(mean_array == 0)
        elif "water_bodies" in f:
            WB = 1*(mean_array < 0.02)
        elif "ws" in f:
            WS = 1*(mean_array > 8.5)

Array = PA+S+UA+WB+WS

# output array as raster
with rasterio.open('./data/data\protected_areas.tif') as raster:
    ras_data = raster.read()
    ras_meta = raster.profile

with rasterio.open("Zoe_Raster.tif", 'w', **ras_meta) as dst:
    dst.write(Array, 1)

count = np.count_nonzero(Array == 5)
print('The number of suitable sites is:', count)

# getting centroid locations for suitable sites

centroids = []

with rasterio.open('./Zoe_Raster.tif') as raster:
    cell_size = raster.transform[0]
    bounds = raster.bounds
    x_coords = np.arange(bounds[0] + cell_size/2, bounds[2], cell_size)
    y_coords = np.arange(bounds[1] + cell_size/2, bounds[3], cell_size)
    x, y = np.meshgrid(x_coords, y_coords)        
    coords = np.c_[x.flatten(), y.flatten()]

    where = np.where(Array == 5)
    for idx, value in enumerate(where[0]):
        centroids.append((coords[where[0][idx]][0], coords[where[1][idx]][1]))

# getting coordinates for transmission stations
file = open(PATH2, 'r')
data = file.read()
list = data.split("\n")
coords = []
for l in list[1:-1]:
    a = l.split(',')
    x = float(a[0])
    y = float(a[1])
    coords.append((x,y))

closest_station = []

for cent in centroids:
    list = distance.cdist(coords, [cent], 'euclidean')
    closest_station.append(np.min(list))

print("The shortest distance between the centroid of a suitable site and it's closest transmission station is:", np.min(closest_station))
print("The longest distance between the centroid of a suitable site and it's closest transmission stations is:", np.max(closest_station))
