import urllib.request
import json
import datetime
import time


def get_coord(city):
    url = 'https://geo.api.gouv.fr/communes?nom='+city+'&fields=nom,centre,departement,region&limit=1'
    request = urllib.request.urlopen(url).read()
    data = json.loads(request.decode())
    get_coor = data[0]['centre']['coordinates']
    return get_coor


def bot(user_data):
    user_data = user_data.split(" ")

    #Help
    if user_data[0] == "help":
        return str("Current weather:  'weather' or 'current_weather'\nForecast 1 day: 'forecast'\nForecast 2 day: 'forecast2'\nforecast 7 day: 'daily'")

    #Weather
    if user_data[0] == "weather":
        coord = get_coord(" ".join(user_data[1:]))
        print(coord)

        url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coord[1])+'&lon='+str(coord[0])+'&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode())

        weather = data['weather'][0]['main'], data['weather'][0]['description']
        main = data['main']['temp'],data['main']['feels_like'],data['main']['temp_min'],data['main']['temp_max'], data['main']['pressure'], data['main']['humidity']
        
        return weather[0], weather[1], main[0], main[1], main[2], main[3], main[4], main[5]

    #Forecast hour/hour 1 day
    if user_data[0] == "forecast":
        coord = get_coord(" ".join(user_data[1:]))

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode()) 

        html = ""
        for i in range (int(len(data['hourly'])/2)):
            times = data['hourly'][i]['dt']
            timezone = times + data['timezone_offset']

            forecast_time = datetime.datetime.fromtimestamp(timezone)
            forecast_time = forecast_time.strftime('%d %B %Y - %Hh')
            html += ('<div class="day">' +
                        '<p class="date">' + str(forecast_time) + '</p>' +
                        '<div class="weather">' + 
                            '<img class="weather_icon" src="/app/bot/icons/weather/' + str(data['hourly'][i]['weather'][0]['description']) + '.svg" />' +
                            '<p class="weather_desc">' + str(data['hourly'][i]['weather'][0]['main']) + '</p>' + 
                        '<div>' +
                        '<p class="temperature">Temp:' + str(data['hourly'][i]['temp']) + '°C<p>' +
                        '<p class="feels_like">' + str(data['hourly'][i]['feels_like']) + '<p>' +
                        '<p class="uvi">' + str(data['hourly'][i]['uvi']) + '<p>' +
                    '</div>' + 
                    '<br>')

        return '<div class="forecast">' + html + '</div>'
        

print(bot("forecast cluses"))

"""

#AFFICHAGE VILLE
data[0]['nom'],data[0]['departement']['nom'],data[0]['departement']['code'],data[0]['region']['nom']

#HELP
str("Current weather:  'weather' or 'current_weather'\nForecast 1 day: 'forecast'\nForecast 2 day: 'forecast2'\nforecast 7 day: 'daily'")

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
"""


