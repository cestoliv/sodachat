import urllib.request
import json


#City coordinates (France)

city = str(input("city"))
url = 'https://geo.api.gouv.fr/communes?nom='+str(city)+'&fields=code,nom,centre&limit=1'
request = urllib.request.urlopen(url).read()
data = json.loads(request.decode())

#Current weather

coordinates = data[0]['centre']['coordinates']
url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
request = urllib.request.urlopen(url).read()
data2 = json.loads(request.decode())
print(data2)

print("\n")

main = data2['weather'][0]['main'], data2['weather'][0]['description']
print("Sky :", main[0])
print("Description:", main[1])

current_temp = data2['main']['temp'],data2['main']['feels_like'],data2['main']['temp_min'],data2['main']['temp_max']
print("Current temperature:", current_temp[0],"°C")
print("Feeling:", current_temp[1],"°C")
print("Minimal temperature:", current_temp[2],"°C")
print("Maximal temperature:", current_temp[3],"°C")