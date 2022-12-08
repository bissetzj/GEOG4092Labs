import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
import glob
from rasterstats import zonal_stats

DATA_DIR = './Lab2/lab2/data'  # make this your path to data folder

files = glob.glob(f'{DATA_DIR}/districts/*')

polygons = []
num_coords = []
districts = []

for txt in files:
    file = open(txt, 'r')
    data = file.read()
    list = data.split("\n")
    coords = []
    for l in list[1:]:
        a = l.split("\t")
        x = [float(a[0]), float(a[1])]
        coords.append(x)
    polygons.append(Polygon(coords))
    num_coords.append(len(coords))
    districts.append(txt[-6:-4])

df = {}
df['district'] = districts
df['num_coords'] = num_coords
df['geometry'] = polygons

my_gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
print(f'My geodataframe: \n {my_gdf}')

rasters = glob.glob(f'{DATA_DIR}/agriculture/*.tif')

stats=[]
for r in rasters:
    stats.append(zonal_stats(my_gdf['geometry'], r, categorical=True))

print(f'Raster statistics: \n {stats}')


for i in range(2):
    year = 0
    if i == 0:
        year = '2004'
    elif i == 1:
        year = '2009'
    for j in range(3):
        d = my_gdf['district'][j]
        print(f'# of agricultural pixels (district:{d}, year:{year}): {stats[i][j][1]}.')
        
for i in range(2):
    year = 0
    if i == 0:
        year = '2004'
    elif i == 1:
        year = '2009'
    for j in range(3):
        d = my_gdf['district'][j]
        pd = (stats[i][j][1]) / (stats[i][j][1] + stats[i][j][0])
        pp = round(pd*100, 2)
        print(f'The percent of agricultural land in district {d} in the year {year} is {pp}%.')


    



