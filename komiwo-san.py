import json
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
import shapefile as shp 

#pobranie wymaganych danych z pliku json
data = None
with open('Data\\better_matrix.json', 'r') as dist:
    data = json.load(dist)

city_names = [city["nazwa"] for city in data]
city_coords = [city["koordynaty"] for city in data]
city_dist = [city["odleglosci"] for city in data]
city_demands = [city["zapotrzebowanie"] for city in data]

#konstrukcja prostych klas pomocnych w organizacji danych
@dataclass
class City:
    index: int
    name: list
    
@dataclass
class Path:
    course: list
    length: float = 0

def VRP(city_dist, cars, iterations, cargo, city_demands, alpha, beta, evaporation_rate, Q):

    # inicjalizacja danych początkowych
    cities = city_dist
    n_cities = len(cities)
    city_demands = city_demands
    pheromone = np.ones((n_cities, n_cities))
    best_path_length = np.inf
    best_path = []

    for iteration in range(iterations):
        # inicjacja iteracji
        paths = []
        # stworzenie listy odwiedzonych miast
        visited = [False]*n_cities
        visited[0] = True
    
        for car in range(cars):
            # inicjacja mrówki
            current_point = 0
            path = Path([City(0, city_names[0])])
            # aktualizacja listy odwiedzonych miast
            unvisited = np.where(np.logical_not(visited))[0]
            
            # sprawdzenie czy lista miast nie jest pusta
            if unvisited.tolist() == []:
                # przetransportowanie mrówki do punktu startowego
                next_point = 0
                path.course.append(City(next_point, city_names[next_point]))
                path.length += city_dist[current_point][next_point]
                current_point = next_point
                break
            
            # losowanie punktu startowego
            current_point = np.random.choice(unvisited)
            
            # dodanie wybranego punktu do ścieżki 
            path.course.append(City(current_point, city_names[current_point]))
            path.length += city_dist[0][current_point]

            current_cargo = cargo - city_demands[current_point]
            visited[current_point] = True
            
            # mrówka zaczyna podróż do momentu aż skończy jej się towar lub skończą się miasta do odwiedzenia
            while current_cargo > 0 and False in visited:
                unvisited = np.where(np.logical_not(visited))[0]
                unvisited_cargo = []
                # stworzenie listy miast dla których mrówka ma wystarczająco towaru
                for x in unvisited.tolist():
                    if current_cargo >= city_demands[x]:
                        unvisited_cargo.append(x)
                    
                # sprawdzenie czy lista unvisited cargo nie jest pusta
                if unvisited_cargo == []:
                    # powrót do punktu startowego
                    next_point = 0
                    path.course.append(City(next_point, city_names[next_point]))
                    path.length += city_dist[current_point][next_point]
                    current_point = next_point
                    break
                
                probabilities = np.zeros(len(unvisited_cargo))
                
                #zmiana prawdopodobienstw na podstawie ilosci feromonow na danej sciezce
                for i, unvisited_point in enumerate(unvisited_cargo):
                    probabilities[i] = pheromone[current_point, unvisited_point]**alpha / cities[current_point][unvisited_point]**beta
                
                probabilities /= np.sum(probabilities)
                # wybór następnego miasta na podstawie pozostawionych feromonów
                next_point = np.random.choice(unvisited_cargo, p=probabilities)
                
                path.course.append(City(next_point, city_names[next_point]))
                path.length += city_dist[current_point][next_point]
                
                visited[next_point] = True
                current_point = next_point
                current_cargo -= city_demands[current_point]
            
            #po wykorzystaniu towaru, bądź odwiedzeniu wszystkich miast, mrówka wraca do punktu startowego
            if current_point != 0:
                next_point = 0
                path.course.append(City(next_point, city_names[next_point]))
                path.length += city_dist[current_point][next_point]
                current_point = next_point
                
            paths.append(path)

        #funkcja sprawdza czy nowa sciezka jest lepsza od poprzedniej najlepszej
        if sum([path.length for path in paths]) < best_path_length:
            best_path_length = sum([path.length for path in paths])
            best_path = paths

        #parowanie feromonów
        pheromone *= evaporation_rate

        #ustalenie feromonów na podstawie długości powstałej ścieżki
        for path in paths:
            for i in range(len(path.course)-1):
                pheromone[path.course[i].index, path.course[i+1].index] += Q/path.length
            pheromone[path.course[-1].index, path.course[0].index] += Q/path.length
    
    #formulowanie ostatecznego wyniku
    result_data = {
    "iterations": iterations,
    "alpha": alpha,
    "beta": beta,
    "Q": Q,
    "evaporation rate": evaporation_rate,
    "best path": [[{"name":i.name, "index":int(i.index)} for i in path.course ] for path in best_path],
    "best path length": best_path_length
    }

    return result_data

#funkcja pokazujaca wykres danej trasy
def show_chart(best_path, best_path_length):
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111)

    #rysowanie ksztaltu Polski
    sf = shp.Reader("Poland silhoutte\\A00_Granice_panstwa.shp")
    for shape in sf.shapeRecords():
        x = [i[0] for i in shape.shape.points[:]]
        y = [i[1] for i in shape.shape.points[:]]
    plt.plot(x,y, marker="none")
    
    #naniesienie na mape Polski sciezek znalezionych przez algorytm
    for i in range(len(best_path)):
        xcoords = []
        ycoords = []
        for index, city in enumerate(best_path[i]):
            xcoords.append(city_coords[city["index"]][1])
            ycoords.append(city_coords[city["index"]][0])
            plt.plot(xcoords, ycoords, linestyle='solid', marker="o")
            plt.set_cmap("gist_rainbow")
            plt.title(("Best path length: " + str(best_path_length)))
            plt.xlabel("Longitude")
            plt.ylabel("Latitude")
            if city["index"] == 0:
                ax.annotate(f'{city["name"]}', (city_coords[city["index"]][1], city_coords[city["index"]][0]), weight="bold")
            else:
                ax.annotate(f'{index}. {city["name"]}', (city_coords[city["index"]][1], city_coords[city["index"]][0]))

    plt.show()

#funkcja testująca średnie wartości zwracane przez funkcję
def test(start, end, jump, iterations, test_iterations):
    iteration_chart = []    
    for i in range(start, end, jump):
        suma = 0
        for j in range(0, test_iterations):
            result = VRP(city_dist=city_dist, cars=5, iterations=iterations, cargo=1000, city_demands=city_demands, city_coords=city_coords, alpha=i/100, beta=20, evaporation_rate=0.97, Q=i)
            suma += result["best path length"]
        average = suma/test_iterations
        iteration_chart.append([i, average])
        print(iteration_chart)
    return iteration_chart

best_result = VRP(city_dist=city_dist, cars=5, iterations=5000, cargo=1000, city_demands=city_demands, alpha=0.9, beta=20, evaporation_rate=0.90, Q=1000)
show_chart(best_path=best_result["best path"], best_path_length=best_result["best path length"])

# while best_result["best path length"] > 4100:
#     best_result = VRP(city_dist=city_dist, cars=5, iterations=6000, cargo=1000, city_demands=city_demands, alpha=0.9, beta=20, evaporation_rate=0.95, Q=1000)
#     print(best_result["best path length"])
# with open("Tests\\best_result.json", "w") as w:
#     json.dump(best_result, w, indent= 2)
# sf = shp.Reader("A00_Granice_panstwa.shp")
# plt.figure()
# for shape in sf.shapeRecords():
#     x = [i[0] for i in shape.shape.points[:]]
#     y = [i[1] for i in shape.shape.points[:]]
#     plt.plot(x,y)
# plt.show()


# VRP(city_dist=city_dist, cars=5, iterations=3000, cargo=1000, city_demands=city_demands, city_coords=city_coords, alpha=0.5, beta=20, evaporation_rate=0.90, Q=20)



# alfa_test = test(50, 101, 5, 1000, 20)

# with open("testy_alfa.json", "w") as w:
#     json.dump(alfa_test, w, indent= 2)

# x = []
# y = []


# fig = plt.figure(figsize=(8,6))
# ax = fig.add_subplot(111)
# sf = shp.Reader("A00_Granice_panstwa.shp")
# for shape in sf.shapeRecords():
#     x = [i[0] for i in shape.shape.points[:]]
#     y = [i[1] for i in shape.shape.points[:]]
# plt.plot(x,y, marker="none")




# with open("Tests\\testy_iteracje_funkcja.json", "r") as r:
#     data = json.load(r)
#     for i in range(len(data)-1):
#         x.append(data[i][0])
#         y.append(data[i][1])

# for k in alfa_test:
#     for i in range(len(k)-1):
#         x.append(k[0])
        # y.append(k[1]/100)
# for k in data[-1]:
#     for i in range(len(k)-1):
#         x.append(k[0])
#         y.append(k[1])

# plt.plot(x,y, linewidth=3)
# plt.xlabel('Procent ewaporacji',fontsize=15)
# plt.ylabel('Średnia długość przy 3000 iteracji', fontsize=15)
# plt.title("Stosunek wartości współczynnika ewaporacji do średniej poszukiwanej długości minimalnej", fontsize=20)
# plt.show()

    

# chart_data = test(100, 1001, 100, 30)
# chart_data.append(test(2000,10001,1000, 20))


# plt.plot(x,y, linewidth=3)
# # plt.margins(y)
# plt.xlabel('Liczba iteracji',fontsize=15)
# plt.ylabel('Średnia długość', fontsize=15)
# plt.title("Stosunek ilości iteracji algorytmu do średniej poszukiwanej długości minimalnej", fontsize=20)
# plt.show()



# for i in range(2000, 10001, 1000):
#     print(i)
#     suma = 0
#     for j in range(0, 20):
#         result = VRP(city_dist=city_dist, cars=5, iterations=i, cargo=1000, city_demands=city_demands, city_coords=city_coords, alpha=0.8, beta=20, evaporation_rate=0.90, Q=20)
#         if best_result["best path length"] > result["best path length"]:
#             best_result = result

# print(best_result)


# with open("testy_iteracje.json", "a") as w:
#     json.dump(iteration_test, w, indent= 2) 
# plot_data = []



# with open("testy_iteracje.json" , "r") as r:
#     data = json.load(r)
#     for i in data:
#         print(i["best path length"], i["iterations"])





# with open("wyniki.json", "w") as w:
#     json.dump(result_data, w) 