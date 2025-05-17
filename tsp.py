import csv
import json
from collections import namedtuple
from math import radians, sin, cos, sqrt, atan2
import tempfile

# ------------------ Haversine distance -------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Earth radius in km
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lon2 - lon1)
    a = sin(d_phi/2)**2 + cos(phi1)*cos(phi2)*sin(d_lambda/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

# ------------------ TSP Solver ---------------------------
Place = namedtuple('Place', ['name', 'lat', 'lon'])

def greedy_solver(places, dist, start_idx=0, return_to_start=True):
    n = len(places)
    visited = [False]*n
    path = [start_idx]
    visited[start_idx] = True
    current = start_idx

    for _ in range(n-1):
        next_city = min(
            (j for j in range(n) if not visited[j]),
            key=lambda j: dist[current][j]
        )
        path.append(next_city)
        visited[next_city] = True
        current = next_city

    if return_to_start:
        path.append(start_idx)
    return path

def two_opt(path, dist):
    improved = True
    while improved:
        improved = False
        for i in range(1, len(path)-2):
            for j in range(i+1, len(path)-1):
                if j - i == 1:
                    continue
                l1 = dist[path[i-1]][path[i]] + dist[path[j]][path[j+1]]
                l2 = dist[path[i-1]][path[j]] + dist[path[i]][path[j+1]]
                if l2 < l1:
                    path[i:j+1] = reversed(path[i:j+1])
                    improved = True
    return path

# ------------------ Main code -----------------------------

# Himachal Pradesh places CSV data as string
csv_data = """Name,Lat,Lon
Shimla,31.1048,77.1734
Manali,32.2396,77.1887
Dharamshala,32.2190,76.3234
Kullu,31.9570,77.1090
"""

# Write CSV data to temporary file
with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.csv') as tmp_csv:
    tmp_csv.write(csv_data)
    csv_filename = tmp_csv.name

def read_places(csv_path):
    places = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            places.append(Place(row['Name'], float(row['Lat']), float(row['Lon'])))
    return places

def create_distance_matrix(places):
    n = len(places)
    dist = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i][j] = haversine(places[i].lat, places[i].lon, places[j].lat, places[j].lon)
    return dist

def save_geojson(path_indices, places, filename='route.geojson'):
    coords = [[places[i].lon, places[i].lat] for i in path_indices]
    geojson = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            },
            "properties": {
                "name": "TSP route"
            }
        }]
    }
    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)
    print(f"GeoJSON route saved to: {filename}")

def main():
    places = read_places(csv_filename)
    dist = create_distance_matrix(places)

    # Start at Shimla (index 0)
    start_idx = 0
    path = greedy_solver(places, dist, start_idx=start_idx, return_to_start=True)
    path = two_opt(path, dist)

    print("Optimal tour:")
    for i, idx in enumerate(path):
        print(f"{i+1}) {places[idx].name}")
    total_dist = sum(dist[path[i]][path[i+1]] for i in range(len(path)-1))
    print(f"Total distance: {total_dist:.2f} km")

    save_geojson(path, places)

if __name__ == '__main__':
    main()
