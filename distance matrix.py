#distance matrix

from scipy.spatial import distance
import numpy as np
from haversine import haversine
import json



coords = []
miasta = []
zapo = []
with open('convert.json') as c:
    data = json.load(c)
    for i in data:
        coords.append(data[i])
        miasta.append(i)

with open('zapotrzebowanie.txt') as z:
    for row in z:
        zapo.append(row)


dist_matrix = distance.cdist(coords, coords, metric=haversine)
btr_matrix = []
for i in range(len(dist_matrix)):
    btr_matrix.append(
    {"nazwa": miasta[i],
    "koordynaty": coords[i],
    "odleglosci": dist_matrix[i].tolist(),
    "odleglosci + miasta": {miasta[j]:dist_matrix[i].tolist()[j] for j in range(len(dist_matrix[i]))},
    "zapotrzebowanie": int(zapo[i])}
    )

with open('better_matrix.json', 'w') as dist:
    json.dump(btr_matrix, dist, indent=2)



""" data = None
with open('convert.json', 'r') as _file:
    data = json.load(_file)

data2 = {}
for i in data:
    data2[i] = {"Latitude" : data[i][0], "Longitude" : data[i][1]}
    

with open('data.json', 'w') as _file:
    json.dump(data2, _file, indent=2) """