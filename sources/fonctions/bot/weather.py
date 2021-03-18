import urllib.request
import json


#City coordinates(France)

city = str(input("city"))
url = 'https://geo.api.gouv.fr/communes?nom='+str(city)+'&fields=code,nom,centre&limit=1'
request = urllib.request.urlopen(url).read()
data = json.loads(request.decode())
print(data)


#Current weather

coordinates = data[0]['centre']['coordinates']
url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coordinates[0])+'&lon='+str(coordinates[1])+'&appid=05c0f1a3f5fd53306747862f8372e8fb'
request = urllib.request.urlopen(url).read()
data2 = json.loads(request.decode())
print(data2)