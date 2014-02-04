#!/usr/bin/python

import urllib2,datetime

#Set thresholds
windThresh = 20.
tempThresh = 50. 

#Define Good Conditions
goodCons = ['Clear','Scattered Clouds','Partly Cloudy', 'Sunny', 'Mostly Sunny', 'Few Clouds']

#### #### #### Today's Weather #### #### ####
# TimeLocal,TemperatureF,Dew PointF,Humidity,Sea Level PressureIn,VisibilityMPH,Wind Direction,Wind SpeedMPH,Gust SpeedMPH,PrecipitationIn,Events,Conditions,WindDirDegrees,DateUTC
def getCurrentWeather(locationName, now):
# Open wunderground.com url
    url_weather = "http://www.wunderground.com/history/airport/%s/%s/%s/%s/DailyHistory.html?theprefset=SHOWMETAR&theprefvalue=1&format=1" %(str(locationName), str(now.year), str(now.month), str(now.day))

    try: 
        u_w = urllib2.urlopen(url_weather)
    except urllib2.URLError:
        end()
    else:
        data = u_w.read().split('<br />')[1:]
        data_weather = [s.strip('\n').split(',') for s in data[:-1]]

    try:
        data_weather[-1]
    except IndexError:
        return "It's midnight. Go to sleep."
        exit()
        #It's around midnight and there hasn't been a reading yet.
    else:
        return data_weather[-1]


#### #### #### SUNRISE AND SUNSET #### #### ####
# Get sunrise and sunset times
#l=2465887;curl -s |sed -n 's/.*sunrise="\([0-9:]\{1,\}\).*="\([0-9:]\{1,\}\).*/\1 \2/p'

def getSunriseSunset(locationID):
    url_astro = "http://weather.yahooapis.com/forecastrss?w=" + str(locationID)
    try: 
        u_a = urllib2.urlopen(url_astro)
    except urllib2.URLError:
        end()
    else:
        data = u_a.read().split('<br />')
        data_astro = [s.strip('\n').split('\n') for s in data]

    #Returns a list of two strings, ['<sunrise>','<sunset>']
    #240 character lines? Ain't nobody got screens fo' that.
    #The 12 is to convert into 24 hour time if the string originally had 'pm' in it
    return [i.strip(' am') if ' am' in i else ':'.join([str(int(str(i).strip(' pm').split(':')[0])+12),str(i).strip(' pm').split(':')[1]]) for i in str([i for i in data_astro[0] if i.startswith('<yweather:astronomy')]).split('"')[1::2]]    


#### #### #### PROCESSING #### #### ####
# Shove it in a dictionary:
# TimeLocal,TemperatureF,Dew PointF,Humidity,Sea Level PressureIn,...
# VisibilityMPH,Wind Direction,Wind SpeedMPH,Gust SpeedMPH,PrecipitationIn,...
# Events,Conditions,WindDirDegrees,DateUTC

# Daylight
def daylightTest(datetime_local_string, locationID):

    # Get sunrise, sunset
    sunrise, sunset = getSunriseSunset(locationID)

    format_local_in = '%I:%M %p'
    
    # Do the test
    current_time=datetime.datetime.strptime(datetime_local_string, format_local_in)
        
    format_sun_in = '%H:%M'
    
    today_rise_time = datetime.datetime.strptime(sunrise, format_sun_in)
    today_set_time = datetime.datetime.strptime(sunset, format_sun_in)
        
    # It's dark if it's not light
    if ( today_rise_time <= current_time ) and ( current_time <= today_set_time ):
        return 'Light'
    else:
        return 'Dark'
        
# Winds
def windTest(gust_speed):
    try:
        return float(gust_speed)
    except ValueError:
        return 'NaN'

# Temperature
def tempTest(temp_F):
    try:
        return float(temp_F)
    except ValueError:
        return 'NaN'

# Clouds
'''
def cloudTest(conditions):
    if conditions not in goodCons:
        return 'Cloudy'
    else:
        return 'OK'
'''

# Clean up missing values?
#todayData= todayData.replace('-9999', 'NaN')


#### #### Jumpability Test #### ####
def jumpTest(all_tests):
    if all_tests['Daylight']=='Light' and all_tests['Winds'] <= windThresh and all_tests['Temperature'] >= tempThresh and all_tests['Clouds'] in goodCons:
        return 'YES'
    else:
        return 'NO'


#### #### Final Analysis #### ####
def finalPrint(out):
    return ' '.join(map(str,out.values()))
#    return outputConds['Daylight'] + ' ' + outputConds['Winds'] + ' ' + outputConds['Temperature'] + ' ' + outputConds['Clouds'] + ' ' + outputConds['Jumpable']


def getConditions(locationName,locationID):
    now = datetime.datetime.now()

    data_weather = getCurrentWeather(locationName, now)
    keyList = ['TimeLocal','TemperatureF','Dew PointF','Humidity','Sea Level PressureIn','VisibilityMPH','Wind Direction','Wind SpeedMPH','Gust SpeedMPH','PrecipitationIn','Events','Conditions','WindDirDegrees','DateUTC']
    todayData = {keyList[i]: data_weather[i] for i in range(len(keyList))}

    todayData['Daylight']=daylightTest(todayData['TimeLocal'], locationID)

    if (todayData['Gust SpeedMPH'] == '-') or (todayData['Gust SpeedMPH'] == 'Calm'):
        todayData['Gust SpeedMPH'] = float(0.0)
    todayData['Winds'] = windTest(todayData['Gust SpeedMPH'])

    todayData['Temperature'] = tempTest(todayData['TemperatureF'])

    todayData['Clouds'] = todayData['Conditions']

    importantValues = {k: todayData[k] for k in ['Daylight', 'Winds', 'Temperature', 'Clouds']}
    todayData['Jumpable'] = jumpTest(importantValues)

    finalDict = {k: todayData[k] for k in ['Daylight', 'Winds', 'Temperature', 'Clouds', 'Jumpable']}
    todayData['Finalout'] = finalPrint(finalDict)

    finalDict['Sample Time'] = todayData['TimeLocal']

    #conditionString = ''.join(["\n%s:%s"%(i,finalDict[i]) for i in finalDict])
# Output
    return finalDict
    #return 'At %s as of %s:\n%s%s' %(str(locationName),timeofCheck,jumpingStatus,conditionString)

if __name__ == '__main__': print "Test mode:\n", getConditions('KORE',2465887)
