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
if user_data == 'weather' or user_data == 'current_weather':

    url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data2 = json.loads(request.decode())

    weather = data2['weather'][0]['main'], data2['weather'][0]['description']
    print(" Sky :", weather[0],"\n", "Description:", weather[1])

    main = data2['main']['temp'],data2['main']['feels_like'],data2['main']['temp_min'],data2['main']['temp_max'], data2['main']['pressure'], data2['main']['humidity']
    print(" Current temperature:", main[0],"°C","\n","Feeling:", main[1],"°C","\n","Minimal temperature:", main[2],"°C","\n","Maximal temperature:", main[3],"°C","\n","Pressure:",main[4],"hPa","\n","Humidity:",main[5],"%","\n")


#Forecast hour/hour 1 day
if user_data == 'forecast' or user_data == 'forecastoneday':

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode())
    
    day = len(data3['hourly'])/2 #only want 24 hours forecast
    
    for i in range (int(day)):
        datetime = int(data3['hourly'][i]['dt']) + 3600
        url = 'https://showcase.api.linx.twenty57.net/UnixTime/fromunixtimestamp?unixtimestamp='+str(datetime) #GMT GreenWich +1 hour for Paris/Geneva
        request = urllib.request.urlopen(url).read()
        data4 = json.loads(request.decode())
        print(str(data4['Datetime']), ": \n", "Weather:", str(data3['hourly'][i]['weather'][0]['main']),"\n", "Temperature:", str(data3['hourly'][i]['temp'])+ "°C (feeling:", str(data3['hourly'][i]['feels_like'])+"°C)", "\n", "UV index:", str(data3['hourly'][i]['uvi']), "\n")


#Forecast hour/hour 2 day
if user_data == 'forecast2' or user_data == 'forecasttwoday':

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode())
    
    for i in range (len(data3['hourly'])):
        datetime = int(data3['hourly'][i]['dt']) + 3600
        url = 'https://showcase.api.linx.twenty57.net/UnixTime/fromunixtimestamp?unixtimestamp='+str(datetime) #GMT GreenWich +1 hour for Paris/Geneva
        request = urllib.request.urlopen(url).read()
        data4 = json.loads(request.decode())
        print(str(data4['Datetime']), ": \n", "Weather:", str(data3['hourly'][i]['weather'][0]['main']),"\n", "Temperature:", str(data3['hourly'][i]['temp'])+ "°C (feeling:", str(data3['hourly'][i]['feels_like'])+"°C)", "\n", "UV index:", str(data3['hourly'][i]['uvi']), "\n")
    

#Alerts
if user_data == 'alerts':

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=daily,current,hourly,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode())
    print(" Alerts",data3['alerts'][0]['sender_name'],":", data3['alerts'][0]['description'], "\n Events:", data3['alerts'][0]['event'])


#Daily
if user_data == 'daily':

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=alerts,current,hourly,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode())
    print(data3)

    for i in range (len(data3['daily'])):
        datetime = int(data3['daily'][i]['dt']) + 3600
        url = 'https://showcase.api.linx.twenty57.net/UnixTime/fromunixtimestamp?unixtimestamp='+str(datetime) #GMT GreenWich +1 hour for Paris/Geneva
        request = urllib.request.urlopen(url).read()
        data4 = json.loads(request.decode())
        print(data4['Datetime']+":")

#trouver un moyen de convertir le format de la date 
#ex: 2021-03-27 12:00:00 -> Samedi 27 mars 2021 12:00
#pour obtenir lecture plus agreable des données notement pour 'sunset' & 'sunrise'  
#ne donner que l'heure de lever et de coucher plutot que toute la date