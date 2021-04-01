import urllib.request
import json
import datetime
import time



def bot(user_data):
    user_data = user_data.split(" ")

    #Help
    if(user_data_split[0] == "help"):
        return "Current weather:  'weather' or 'current_weather'\nForecast 1 day: 'forecast'\nForecast 2 day: 'forecast2'\nforecast 7 day: 'daily'"


    if(user_data_split[0] == "weather"):
        url = 'https://geo.api.gouv.fr/communes?nom='+str(city)+'&fields=nom,centre,departement,region&limit=1'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode())
        coordinates = data[0]['centre']['coordinates']
        return coordinates
      




def get_coord(city):
    url = 'https://geo.api.gouv.fr/communes?nom='+str(city)+'&fields=nom,centre,departement,region&limit=1'
    request = urllib.request.urlopen(url).read()
    data = json.loads(request.decode())
    coordinates = data[0]['centre']['coordinates']
    return coordinates


#City coordinates (France)
city = str(input("city"))

print("\n",data[0]['nom']+",",data[0]['departement']['nom'],"("+data[0]['departement']['code']+"),",data[0]['region']['nom']+":","\n")

#User request (provisional)
user_data = str(input("data"))

#Help command
if user_data == 'help':
    print("Current weather:  'weather' or 'current_weather'\nForecast 1 day: 'forecast'\nForecast 2 day: 'forecast2'\nforecast 7 day: 'daily'")

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
if user_data == 'forecast':

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode()) 
    day = len(data3['hourly'])/2

    for i in range (int(day)):
        times = data3['hourly'][i]['dt']
        timezone = times + data3['timezone_offset']

        forecast_time = datetime.datetime.fromtimestamp(timezone)
        forecast_time = forecast_time.strftime('%d %B %Y - %Hh:')
        print(str(forecast_time), "\n", "Weather:", str(data3['hourly'][i]['weather'][0]['main']),"\n", "Temperature:", str(data3['hourly'][i]['temp'])+ "°C (feeling:", str(data3['hourly'][i]['feels_like'])+"°C)", "\n", "UV index:", str(data3['hourly'][i]['uvi']), "\n")
    

#Forecast hour/hour 2 day
if user_data == 'forecast2': 

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode()) 

    for i in range (int(day)):
        times = data3['hourly'][i]['dt']
        timezone = times + data3['timezone_offset']

        forecast_time = datetime.datetime.fromtimestamp(timezone)
        forecast_time = forecast_time.strftime('%d %B %Y - %Hh:')
        print(str(forecast_time), "\n", "Weather:", str(data3['hourly'][i]['weather'][0]['main']),"\n", "Temperature:", str(data3['hourly'][i]['temp'])+ "°C (feeling:", str(data3['hourly'][i]['feels_like'])+"°C)", "\n", "UV index:", str(data3['hourly'][i]['uvi']), "\n")


#Daily
if user_data == 'daily':

    url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coordinates[1])+'&lon='+str(coordinates[0])+'&exclude=alerts,current,hourly,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
    request = urllib.request.urlopen(url).read()
    data3 = json.loads(request.decode())
    print(data3)

    for i in range (len(data3['daily'])):
    
        #Timezone
        times = data3['daily'][i]['dt']
        timezone = times + data3['timezone_offset']
        forecast_time = datetime.datetime.fromtimestamp(timezone)
        forecast_time = forecast_time.strftime('%a %d %B:')

        #Sunrise 
        sunrise = data3['daily'][i]['sunrise']
        sunrise_time = datetime.datetime.fromtimestamp(sunrise)
        sunrise_time = sunrise_time.strftime('%H:%M')

        #Sunset
        sunset = data3['daily'][i]['sunset']
        sunset_time = datetime.datetime.fromtimestamp(sunset)
        sunset_time = sunset_time.strftime('%H:%M')

        print(str(forecast_time),"\nWeather:",data3['daily'][i]['weather'][0]['main'],"\nSunrise:",str(sunrise_time),"   Sunset:",str(sunset_time),"\nMin:",data3['daily'][i]['temp']['min'],"°C    Max:",data3['daily'][i]['temp']['max'],"°C   Day:",data3['daily'][i]['temp']['day'],"°C\n")
