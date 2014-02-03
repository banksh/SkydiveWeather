#!/usr/bin/python

import urllib2,datetime

# KORE
locationName='KORE'
#obs.lat = '42.57' #+N
#obs.long= '-72.2885' #+E
#utc_zone = tz.gettz('UTC')
#local_zone = tz.gettz('America/New_York')
#timeKey_options = ["TimeEST", "TimeEDT"]
#locationID = 2465890 #FYI this is Orange, California
locationID = 2465887 #FYI I was totally testing you, this is Orange, MA

#Set thresholds
#Degrees F and mph
windThresh = 20.
tempThres = 50. 

# Set acceptable conditions
goodCons = ['Clear','Scattered Clouds','Partly Cloudy', 'Sunny', 'Mostly Sunny', 'Few Clouds']

# Get today's date
now = datetime.datetime.now()

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
        data = [s.strip('\n').split(',') for s in data[:-1]]
        #data_weather = [{s[0]:s[1:]} for s in data]
        data_weather = data

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
    #The 12 is to convert into 24 hour time if the string originally had 'pm' in it
    return [i.strip(' am') if ' am' in i else ':'.join([str(int(str(i).strip(' pm').split(':')[0])+12),str(i).strip(' pm').split(':')[1]]) for i in str([i for i in data_astro[0] if i.startswith('<yweather:astronomy')]).split('"')[1::2]]    


#### #### #### PROCESSING #### #### ####
# Shove it in a dictionary:
# TimeLocal,TemperatureF,Dew PointF,Humidity,Sea Level PressureIn,...
# VisibilityMPH,Wind Direction,Wind SpeedMPH,Gust SpeedMPH,PrecipitationIn,...
# Events,Conditions,WindDirDegrees,DateUTC

data_weather = getCurrentWeather(locationName, now)
keyList = ['TimeLocal','TemperatureF','Dew PointF','Humidity','Sea Level PressureIn','VisibilityMPH','Wind Direction','Wind SpeedMPH','Gust SpeedMPH','PrecipitationIn','Events','Conditions','WindDirDegrees','DateUTC']
todayData = {keyList[i]: data_weather[i] for i in range(len(keyList))}

# Daylight
def daylightTest(datetime_local_string):

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

todayData['Daylight']=daylightTest(todayData['TimeLocal'])

# Winds
def windTest(gust_speed):
    try:
        return float(gust_speed)
    except ValueError:
        return 'NAN'

if todayData['Gust SpeedMPH'] == '-':
    todayData['Gust SpeedMPH'] == float(0.0)
todayData['Winds'] = windTest(todayData['Gust SpeedMPH'])

# Temperature
def tempTest(temp_F):
    try:
        return float(temp_F)
    except ValueError:
        return 'NaN'

# Unecessary if test? 
if todayData['TemperatureF'] == '':
    todayData['TemperatureF'] == 'NaN'
todayData['Temperature'] = tempTest(todayData['TemperatureF'])

# Clouds
'''
def cloudTest(conditions):
    if conditions not in ['Clear', 'Scattered Clouds', 'Partly Cloudy', 'Sunny', 'Mostly Sunny', 'Few Clouds']:
        return 'Cloudy'
    else:
        return 'OK'
'''

todayData['Clouds'] = todayData['Conditions']

# Clean up missing values ?
#todayData= todayData.replace('-9999', 'NaN')

#### #### Jumpability Test #### ####
def jumpTest(all_tests):
    if all_tests['Daylight']=='Light' and all_tests['Winds'] <= windThresh and all_tests['Temperature'] >= tempThresh and all_tests['Clouds'] in goodCons:
        return 'YES'
    else: return 'NO'

importantValues = {k: todayData[k] for k in ['Daylight', 'Winds', 'Temperature', 'Clouds']}
todayData['Jumpable'] = jumpTest(importantValues)


# Final Analysis
def finalPrint(out):
    return ' '.join(map(str,out.values()))


# THIS IS MESSY SYNTAX AND SLOPPY CODING
finalDict = {k: todayData[k] for k in ['Daylight', 'Winds', 'Temperature', 'Clouds', 'Jumpable']}
todayData['Finalout'] = finalPrint(finalDict)

if 'YES' in todayData['Finalout']:
    jumpingStatus = ['YES', 'Go Jumping!']
else:
    jumpingStatus = todayData['Finalout'] 
    
    
# Output
# SLOPPY
timeofCheck = todayData['TimeLocal']

print 'At %s as of %s:' %(str(locationName),timeofCheck)
if 'NO' in jumpingStatus:
    print "Don't jump!:",
print''.join(["%s:%s "%(i,finalDict[i]) for i in finalDict])

