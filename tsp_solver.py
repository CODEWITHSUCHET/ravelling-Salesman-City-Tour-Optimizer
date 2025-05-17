from collections import namedtuple

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
        for i in range(1, len(path) - 2):
            for j in range(i+1, len(path) - 1):
                if j - i == 1:
                    continue
                l1 = dist[path[i-1]][path[i]] + dist[path[j]][path[j+1]]
                l2 = dist[path[i-1]][path[j]] + dist[path[i]][path[j+1]]
                if l2 < l1:
                    path[i:j+1] = reversed(path[i:j+1])
                    improved = True
    return path
