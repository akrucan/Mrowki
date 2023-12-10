from geopy.geocoders import Nominatim
import json 

r = open("miasta.txt", "r", encoding="utf-8")

coordinates = {}

geolocator = Nominatim(user_agent="mrowkex")
for x in r:
    print(x)
    location = geolocator.geocode(x,timeout=10000)
    coordinates[x.strip("\n")] = (location.latitude, location.longitude)
print(coordinates)

# r = open("convert.json", "r", encoding="utf-8")
# data = json.load(r)
# for i in data:
#     print(data[i])
with open('convert.json', 'w', encoding="utf-8") as convert_file: 
     convert_file.write(json.dumps(coordinates))
r.close
