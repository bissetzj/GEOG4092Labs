import fiona
import geopandas as gpd
import pandas as pd
import random
from shapely.geometry import Point

random.seed(0)
DATA_DIR = "./Lab3/lab3.gpkg"  # make this your path to geopackage 

layers = fiona.listlayers(DATA_DIR)
print(layers)

def random_sample(name, number):
    """
    Takes a layer from a geopackage and finds n for each polygon, which is the number of 
    points in the area with a point density of 0.05 points/sqkm. 
    Then creates a stratified random sample of n points in each polygon. 

    Args:
        name (str) = layername in geopackage
        number (str) = column name that contains watershed code (either "HUC8" or "HUC12")

    Returns:
        sample_points = a geodataframe with the sampled points

    """
    huc = gpd.read_file(DATA_DIR, layer = name)
    sample_points = {'point_id': [], 'geometry': [], 'HUC8': []}
    for idx, row in huc.iterrows():
        bounds = huc.loc[[idx], 'geometry'].total_bounds
        areasqkm = huc.loc[[idx], 'geometry'].area/ 10**6
        n = int(round(areasqkm*0.05))
        for i in range(n):
            intersects = False
            while intersects == False:
                x = random.uniform(bounds[0], bounds[2])
                y = random.uniform(bounds[1], bounds[3])
                point = Point(x,y)

                results = huc.loc[[idx], 'geometry'].intersects(point)
                if True in results.unique():
                    sample_points['geometry'].append(Point((x, y)))
                    sample_points['point_id'].append(i)
                    sample_points['HUC8'].append(huc._get_value(idx, number)[0:8])
                    intersects = True
    sample_points = gpd.GeoDataFrame(sample_points)
    return sample_points


sample8 = random_sample("wdbhuc8", "HUC8")
sample12 = random_sample("wdbhuc12", "HUC12")


SSURGO = gpd.read_file(DATA_DIR, layer = 'ssurgo_mapunits_lab3')

join = gpd.sjoin(sample8, SSURGO )
join2 = gpd.sjoin(sample12, SSURGO )

group1 = join.groupby('HUC8').mean()
group2 = join2.groupby('HUC8').mean()

for j in range(2):
    if j == 0:
        df = group1
        sample = "HUC8 sample"
    else:
        df = group2
        sample = "HUC12 sample"
    for i in range(3):
        mean = df.iloc[i]['aws0150']
        if i == 0:
            ws = '10190005'
        elif i ==1:
            ws = '10190006'
        else:
            ws = '10190007'
        print(f'From: {sample}, watershed: {ws}, mean: {mean}')
print("Sampling from HUC12 causes the mean to be more consistent across the three watersheds, since sampling from a greater number of small areas means the points are more uniformly spread out.")

        
