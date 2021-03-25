import urllib.request
import json


#City coordinates (France)
city = str(input("city"))
url = 'https://geo.api.gouv.fr/communes?nom='+str(city)+'&fields=nom,centre,departement,region&limit=1'
request = urllib.request.urlopen(url).read()
data = json.loads(request.decode())
coordinates = data[0]['centre']['coordinates']
print("\n",data[0]['nom']+",",data[0]['departement']['nom'],"("+data[0]['departement']['code']+"),",data[0]['region']['nom']+":","\n")

#User request (provisional)
user_data = str(input("data"))


#Current weather
if user_data == "current_weather" or "weather":

    url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data2 = json.loads(request.decode())

    weather = data2['weather'][0]['main'], data2['weather'][0]['description']
    print("Sky :", weather[0],"\n", "Description:", weather[1])

    main = data2['main']['temp'],data2['main']['feels_like'],data2['main']['temp_min'],data2['main']['temp_max'], data2['main']['pressure'], data2['main']['humidity']
    print("Current temperature:", main[0],"°C","\n","Feeling:", main[1],"°C","\n","Minimal temperature:", main[2],"°C","\n","Maximal temperature:", main[3],"°C","\n","Pressure:",main[4],"hPa","\n","Humidity:",main[5],"%","\n")


#Forecast hour/hour
if user_data == "forecast hour/hour":

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode())

    for i in range (len(data3['hourly'])):
        url = 'https://showcase.api.linx.twenty57.net/UnixTime/fromunixtimestamp?unixtimestamp='+str(data3['hourly'][i]['dt'])
        request = urllib.request.urlopen(url).read()
        data4 = json.loads(request.decode())
        print(str(data4['Datetime']), "\n", "Weather:", str(data3['hourly'][i]['weather'][0]['main']),"\n" "Temperature:", str(data3['hourly'][i]['temp'])+ "°C (feeling: ", str(data3['hourly'][i]['feels_like'])+")","\n")
        