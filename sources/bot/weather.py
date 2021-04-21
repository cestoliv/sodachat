import urllib.request
import json
import datetime
import time

def get_coord(city):
    global city_data
    url = 'https://geo.api.gouv.fr/communes?nom='+city+'&fields=nom,centre,departement,region&limit=1'
    request = urllib.request.urlopen(url).read()
    data = json.loads(request.decode())
    if data != []:
        city_data = data[0]['nom'],data[0]['departement']['nom'],data[0]['departement']['code'],data[0]['region']['nom']
        get_coor = data[0]['centre']['coordinates']
        return get_coor
    else:
        return []


def bot(user_data):
    user_data = user_data.split(" ")

    #Help
    if user_data[0] == "help" or len(user_data) == 1:
        html = ('<i><b>Help command: type command message to show datas about your city</b></i><br>' + '<b>Current weather:</b>  weather + <i>[your city]</i> <br>' + '<b>Forecast 1 day:</b>  forecast + <i>[your city]</i> <br>' + '<b>Forecast 2 day:</b>  forecast2 + <i>[your city]</i> <br>' +'<b>Forecast 1 week:</b>  daily + <i>[your city]</i>') 
        return '<div class="bot_weather help">' + html + '</div>'

    #Weather
    if user_data[0] == "weather":
        coord = get_coord(" ".join(user_data[1:]))

        if coord == []:
            return "<p>Could not find this city (<b>" + " ".join(user_data[1:]) + "</b>)</p>"

        url = 'https://api.openweathermap.org/data/2.5/weather?lat='+str(coord[1])+'&lon='+str(coord[0])+'&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode())
        
        html = ("<b>Current weather at " + city_data[0] + ", " + city_data[1] + "(" + city_data[2] + "), " + city_data[3] + ":</b>" + 
                '<div class="day">' +
                    '<div class="weather">' + 
                        '<img class="weather_icon" src="https://openweathermap.org/img/wn/' + str(data['weather'][0]['icon']) + '.png" />'+ 
                        '<p class="weather_desc"><b>' + str(data['weather'][0]['main']) + '</b></p>' +
                    '</div>' +
                    '<p class><b>🌡 Temperature</b></p>' +
                    '<div class="temperature">' +
                        '<p class="temperature"><b>' + str(data['main']['temp']) + '°C</b></p>' +
                        '<p class="feels_like_temperature"><i>feels like:</i> <b>'+ str(data['main']['feels_like']) + '°C</b></p>' +
                        '<p class="min_temperature"><i>Min:</i> <b>' + str(data['main']['temp_min']) + '°C</b></p>' +
                        '<p class="max_temperature"><i>Max:</i> <b>' + str(data['main']['temp_max']) + '°C</b></p>' +
                    '</div>' +
                    '<p class><b>📍 Informations</b></p>' +
                    '<div class="informations">' +
                        '<p class="pressure"><i>Pressure:</i> <b>' + str(data['main']['pressure']) + 'hPa</b></p>' +
                        '<p class="humidity"><i>Humidity:</i> <b>' + str(data['main']['humidity']) + '%</b></p>' +
                    '<div/>' +
                '</div>' + 
                '<br>')

        return '<div class="bot_weather weather">' + html + '</div>'
    

    #Forecast hour/hour 1 day
    if user_data[0] == "forecast":
        coord = get_coord(" ".join(user_data[1:]))

        if coord == []:
            return "<p>Could not find this city (<b>" + " ".join(user_data[1:]) + "</b>)</p>"

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode()) 

        html = "<b>Forecast 1 day at " + city_data[0] + ", " + city_data[1] + "(" + city_data[2] + "), " + city_data[3] + ":</b>"

        html += '<div class="days">'

        # alternate to show 1 of 2
        show = True
        for i in range (int(len(data['hourly'])/2)):
            if not show:
                show = True
            else:
                show = False
                times = data['hourly'][i]['dt']
                timezone = times + data['timezone_offset']

                forecast_time = datetime.datetime.fromtimestamp(timezone)
                forecast_time = forecast_time.strftime('%Hh')
                html += ('<div class="day">' +
                            '<div class="weather">' +
                                '<p class="time">' + str(forecast_time) + '</p>' +
                                '<img class="weather_icon" src="https://openweathermap.org/img/wn/' + str(data['hourly'][i]['weather'][0]['icon']) + '.png" />'+ 
                            '</div>' +
                            '<div class="infos">' +
                                '<p class="weather_desc"><b>' + str(data['hourly'][i]["weather"][0]['main']) + '</b></p>' +
                                '<p class="temperature">' + str(data['hourly'][i]['temp']) + '°C</p>' +
                            '</div>' +
                        '</div>')

        html += '</div>'

        return '<div class="bot_weather forecast">' + html + '</div>'
        
    #Forecast hour/hour 2 day
    if user_data[0] == "forecast2":
        coord = get_coord(" ".join(user_data[1:]))

        if coord == []:
            return "<p>Could not find this city (<b>" + " ".join(user_data[1:]) + "</b>)</p>"

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=daily,current,alerts,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode()) 
        
        html = "<b>Forecast 2 day at " + city_data[0] + ", " + city_data[1] + "(" + city_data[2] + "), " + city_data[3] + ":</b>"
        html += '<div class="days">'

        # alternate to show 1 of 2
        show = True
        for i in range (int(len(data['hourly']))):
            if not show:
                show = True
            else:
                show = False
            
                times = data['hourly'][i]['dt']
                timezone = times + data['timezone_offset']

                forecast_time = datetime.datetime.fromtimestamp(timezone)
                forecast_time = forecast_time.strftime('%Hh')
                html += ('<div class="day">' +
                                '<div class="weather">' +
                                    '<p class="time">' + str(forecast_time) + '</p>' +
                                    '<img class="weather_icon" src="https://openweathermap.org/img/wn/' + str(data['hourly'][i]['weather'][0]['icon']) + '.png" />'+ 
                                '</div>' +
                                '<div class="infos">' +
                                    '<p class="weather_desc"><b>' + str(data['hourly'][i]["weather"][0]['main']) + '</b></p>' +
                                    '<p class="temperature">' + str(data['hourly'][i]['temp']) + '°C</p>' +
                                '</div>' +
                            '</div>')

        html += "</div>"

        return '<div class="bot_weather forecast">' + html + '</div>'
    
    #Daily
    if user_data[0] == 'daily':
        coord = get_coord(" ".join(user_data[1:]))

        if coord == []:
            return "<p>Could not find this city (<b>" + " ".join(user_data[1:]) + "</b>)</p>"

        url = 'https://api.openweathermap.org/data/2.5/onecall?lat='+str(coord[1])+'&lon='+str(coord[0])+'&exclude=alerts,current,hourly,minutely&appid=05c0f1a3f5fd53306747862f8372e8fb&units=metric'
        request = urllib.request.urlopen(url).read()
        data = json.loads(request.decode())

        html = "<b>Forecast 1 week at " + city_data[0] + ", " + city_data[1] + "(" + city_data[2] + "), " + city_data[3] + ":</b>"
        html += '<div class="days">'
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
                            '<img class="weather_icon" src="https://openweathermap.org/img/wn/' + str(data['daily'][i]['weather'][0]['icon']) + '.png" />'+ 
                            '<p class="weather_desc"><b>' + str(data['daily'][i]['weather'][0]['main']) + '</b></p>' +
                        '</div>' +
                        '<div class="infos">' +
                            '<p class="suntime">🌄 ' + str(sunrise_time) + ' 🌇 ' + str(sunset_time) + '</p>' +
                            '<p class="temperature">🌡 ' + str(data['daily'][i]['temp']['day']) + '°C</p>' +
                            '<p class="temperature_min">➖ ' + str(data['daily'][i]['temp']['min']) + '°C</p>' +
                            '<p class="temperature_max">➕ ' + str(data['daily'][i]['temp']['max']) + '°C</p>' +
                        '</div>' +
                    '</div>')

        html += "</div>"

        return '<div class="bot_weather daily">' + html + '</div>'