import urllib.request
import json
import datetime
import time


def get_coord(city):
    url = 'https://geo.api.gouv.fr/communes?nom='+city+'&fields=nom,centre,departement,region&limit=1'
    request = urllib.request.urlopen(url).read()
    data = json.loads(request.decode())
    city_data = data[0]['nom'],data[0]['departement']['nom'],data[0]['departement']['code'],data[0]['region']['nom']
    get_coor = data[0]['centre']['coordinates']
    return get_coor


def bot(user_data):
    user_data = user_data.split(" ")

    #Help
    if user_data[0] == "help":
        html = ('<i><b>Help command: type command message to show datas about your city</b></i><br>' + '<b>Current weather:</b>  weather + <i>[your city]</i> <br>' + '<b>Forecast 1 day:</b>  forecast + <i>[your city]</i> <br>' + '<b>Forecast 2 day:</b>  forecast2 + <i>[your city]</i> <br>' +'<b>Forecast 1 week:</b>  daily + <i>[your city]</i>') 
        return '<div class="help">' + html + '</div>'

    #Weather
    if user_data[0] == "weather":
        coord = get_coord(" ".join(user_data[1:]))
        html = "<b>Current weather at" + "</b><br>" + ""

        url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coord[1])+'&lon='+str(coord[0])+'&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode())
        
        html += ('<div class="day">' +
                        '<div class="weather">' + 
                            '<p class="weather_desc">' + str(data['weather'][0]['main']) +' <img class="weather_icon" src="/app/bot/icons/weather/' + str(data['weather'][0]['icon']) + '.svg" /> </p>'+ 
                        '<div>' +
                        '<p class="temperature">Temp: ' + str(data['main']['temp']) + '°C (feels like:'+ str(data['main']['feels_like']) + '°C)    Min: ' + str(data['main']['temp_min']) + '°C     Max: ' + str(data['main']['temp_max']) + '°C<p>' +
                        '<p class="additionnal">Pressure: ' + str(data['main']['pressure']) + 'hPa     Humidity: ' + str(data['main']['humidity']) + '%<p>' +
                    '</div>' + 
                    '<br>')

        return '<div class="weather">' + html + '</div>'

    #Forecast hour/hour 1 day
    if user_data[0] == "forecast":
        coord = get_coord(" ".join(user_data[1:]))

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode()) 

        
        html = "<b>Forecast 24h at" + "</b><br>" + ""
        for i in range (int(len(data['hourly'])/2)):
            times = data['hourly'][i]['dt']
            timezone = times + data['timezone_offset']

            forecast_time = datetime.datetime.fromtimestamp(timezone)
            forecast_time = forecast_time.strftime('%d %B %Y - %Hh')
            html += ('<div class="day">' +
                        '<p class="date">' + str(forecast_time) + '</p>' +
                        '<div class="weather">' + 
                            '<p class="weather_desc">' + str(data['hourly'][i]['weather'][0]['main']) +' <img class="weather_icon" src="/app/bot/icons/weather/' + str(data['hourly'][i]['weather'][0]['icon']) + '.svg" /> </p>'+ 
                        '<div>' +
                        '<p class="temperature">Temp: ' + str(data['hourly'][i]['temp']) + '°C  (Feels like: ' + str(data['hourly'][i]['feels_like']) + '°C)<p>' +
                        '<p class="uvi">UV index: ' + str(data['hourly'][i]['uvi']) + '<p>' +
                    '</div>' + 
                    '<br>')

        return '<div class="forecast">' + html + '</div>'
        
    #Forecast hour/hour 2 day
    if user_data[0] == "forecast2":
        coord = get_coord(" ".join(user_data[1:]))

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode()) 

        
        html = "<b>Forecast 48h at" + "</b><br>"+ ""
        for i in range (int(len(data['hourly']))):
            times = data['hourly'][i]['dt']
            timezone = times + data['timezone_offset']

            forecast_time = datetime.datetime.fromtimestamp(timezone)
            forecast_time = forecast_time.strftime('%d %B %Y - %Hh')
            html += ('<div class="day">' +
                        '<p class="date">' + str(forecast_time) + '</p>' +
                        '<div class="weather">' + 
                            '<p class="weather_desc">' + str(data['hourly'][i]['weather'][0]['main']) +' <img class="weather_icon" src="/app/bot/icons/weather/' + str(data['hourly'][i]['weather'][0]['icon']) + '.svg" /> </p>'+ 
                        '<div>' +
                        '<p class="temperature">Temp: ' + str(data['hourly'][i]['temp']) + '°C  (Feels like: ' + str(data['hourly'][i]['feels_like']) + '°C)<p>' +
                        '<p class="uvi">UV index: ' + str(data['hourly'][i]['uvi']) + '<p>' +
                    '</div>' + 
                    '<br>')

        return '<div class="forecast2">' + html + '</div>'
    
    #Daily
    if user_data[0] == 'daily':
        coord = get_coord(" ".join(user_data[1:]))

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=alerts,current,hourly,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode())

        html = "<b>Daily data at" + "</b><br>" + ""
        for i in range (len(data['daily'])):
        
            #Timezone
            times = data['daily'][i]['dt']
            timezone = times + data['timezone_offset']
            forecast_time = datetime.datetime.fromtimestamp(timezone)
            forecast_time = forecast_time.strftime('%a %d %B:')

            #Sunrise 
            sunrise = data['daily'][i]['sunrise']
            sunrise_time = datetime.datetime.fromtimestamp(sunrise)
            sunrise_time = sunrise_time.strftime('%H:%M')

            #Sunset
            sunset = data['daily'][i]['sunset']
            sunset_time = datetime.datetime.fromtimestamp(sunset)
            sunset_time = sunset_time.strftime('%H:%M')

            html += ('<div class="day">' +
                        '<p class="date">' + str(forecast_time) + '</p>' +
                        '<div class="weather">' + 
                            '<p class="weather_desc">' + str(data['daily'][i]['weather'][0]['main']) +' <img class="weather_icon" src="/app/bot/icons/weather/' + str(data['daily'][i]['weather'][0]['icon']) + '.svg" /> </p>'+ 
                        '<div>' +
                        '<p class="suntime">Sunrise: ' + str(sunrise_time) + '      Sunset: ' + str(sunset_time) + '<p>' +
                        '<p class="temperature">Min: ' + str(data['daily'][i]['temp']['min']) + '°C     Max:' + str(data['daily'][i]['temp']['max']) + '°C      Day:' + str(data['daily'][i]['temp']['day']) + '°C<p>' +
                    '</div>' + 
                    '<br>')
        return '<div class="daily">' + html + '</div>'


"""
#AFFICHAGE VILLE
data[0]['nom'],data[0]['departement']['nom'],data[0]['departement']['code'],data[0]['region']['nom']
"""



