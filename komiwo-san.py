import json
import matplotlib.pyplot as plt
import numpy as np

data = None
with open('better_matrix.json', 'r') as dist:
    data = json.load(dist)

'''
- liczba samochodów: 5
- pojemość każdego z samochodów: 1000
- liczba klientów, do których należy dostarczyć towar: 30
'''
city_names = [city["nazwa"] for city in data]
city_coords = [city["koordynaty"] for city in data]
city_dist = [city["odleglosci"] for city in data]
city_demands = [city["zapotrzebowanie"] for city in data]
#etc

def mrufki(city_dist, cars, iterations, cargo, city_demands, city_coords, alpha, beta, evaporation_rate, Q):
    starting_point = city_dist[0]
    numer = 0
    cities = city_dist
    n_cities = len(cities)
    city_demands = city_demands
    pheromone = np.ones((n_cities, n_cities))
    best_path_length = np.inf
    best_path = []
    
    for iteration in range(iterations):
        paths = []
        path_lengths = []
        visited = [False]*n_cities
        visited[0] = True
        paths_names = []
        paths_cargo = []
        for car in range(cars):
            # print(visited)
            path = [0]
            path_names = [city_names[0]]
            current_point = 0
            path_length = 0
            path_cargo = []
            unvisited = np.where(np.logical_not(visited))[0]
            # print(unvisited)
            if unvisited.tolist() == []:
                next_point = 0
                path.append(next_point)
                path_names.append(city_names[next_point])
                path_length += city_dist[current_point][next_point]
                current_point = next_point
                break
            current_point = np.random.choice(unvisited)
            path_length = city_dist[0][current_point]
            
            current_cargo = cargo - city_demands[current_point]
            visited[current_point] = True
            path.append(current_point)
            path_names.append(city_names[current_point])
            path_cargo.append(city_demands[current_point])
            
            while current_cargo > 0 and False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                unvisited_cargo = []
                for x in unvisited.tolist():
                    if current_cargo > city_demands[x]:
                        unvisited_cargo.append(x)
                    
                if unvisited_cargo == []:
                    next_point = 0
                    path.append(next_point)
                    path_names.append(city_names[next_point])
                    path_length += city_dist[current_point][next_point]
                    current_point = next_point
                    break
                
                probabilities = np.zeros(len(unvisited_cargo))
                
                for i, unvisited_point in enumerate(unvisited_cargo):
                    probabilities[i] = pheromone[current_point, unvisited_point]**alpha / cities[current_point][unvisited_point]**beta
                
                probabilities_test = probabilities
                probabilities /= np.sum(probabilities)
                try:
                    next_point = np.random.choice(unvisited_cargo, p=probabilities)
                except(ValueError):
                    print(numer, path_names, unvisited_cargo, probabilities, probabilities_test, unvisited, pheromone[current_point, unvisited_point]**alpha, cities[current_point][unvisited_point]**beta, pheromone[current_point, unvisited_point]**alpha / cities[current_point][unvisited_point]**beta)
                    raise
                path.append(next_point)
                path_names.append(city_names[next_point])
                path_cargo.append(city_demands[next_point])
                path_length += city_dist[current_point][next_point]
                visited[next_point] = True
                current_point = next_point
                current_cargo -= city_demands[current_point]
            
            if current_point != 0:
                next_point = 0
                path.append(next_point)
                path_names.append(city_names[next_point])
                path_length += city_dist[current_point][next_point]
                current_point = next_point
                


            paths.append(path)
            paths_names.append(path_names)
            paths_cargo.append(path_cargo)
            path_lengths.append(path_length)
        
        """ for i in paths_cargo:
            print(sum(i)) """
        
        path_length = sum(path_lengths)

        if path_length < best_path_length:
            best_path_length = path_length
            best_path = paths

        pheromone *= evaporation_rate
        
        for path, path_length in zip(paths, path_lengths):
            for i in range(len(path)-1):
                pheromone[path[i], path[i+1]] += Q/path_length
            pheromone[path[-1], path[0]] += Q/path_length

        numer += 1
    
    """ result_data = {
    "iterations": int(iterations),
    "alpha": alpha,
    "beta": beta,
    "Q": int(Q),
    "evaporation rate": evaporation_rate,
    "best path": best_path,
    "best path length": best_path_length
    }

    with open("wyniki.json", "w") as w:
        json.dump(result_data, w) """

    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)

    for i in range(len(best_path)):
        xcoords = []
        ycoords = []
        for j in best_path[i]:
            xcoords.append(city_coords[j][1])
            ycoords.append(city_coords[j][0])
            plt.plot(xcoords, ycoords)
            plt.title(("Best path length: " + str(best_path_length)))
            ax.annotate(city_names[j], (city_coords[j][1], city_coords[j][0]))
        
    plt.show()
                


mrufki(city_dist, 5, 3000, 1000, city_demands, city_coords, 0.7, 30, 0.8, 500)