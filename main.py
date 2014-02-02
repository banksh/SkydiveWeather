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



# Get today's date
now = datetime.datetime.now()

####### Today's Weather #######
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


####### SUNRISE AND SUNSET ####### 
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
<<<<<<< HEAD
	#Jesus Christ this is like a whole fucking program in itself. 
	#240 character lines? Ain't nobody got screens fo' that.
	#Does it seriously add a hardcoded "12"?
	#The 12 is to convert into 24 hour time if the string originally had 'pm' in it
=======
	#Converts to 24 hour clock by adding 12 to pm.
	#A 240 character line? Ain't nobody got screens fo' that.
>>>>>>> now working except for the final print
	return [i.strip(' am') if ' am' in i else ':'.join([str(int(str(i).strip(' pm').split(':')[0])+12),str(i).strip(' pm').split(':')[1]]) for i in str([i for i in data_astro[0] if i.startswith('<yweather:astronomy')]).split('"')[1::2]]	

######################## PROCESSING ########################
# Shove it in a dictionary:
# TimeLocal,TemperatureF,Dew PointF,Humidity,Sea Level PressureIn,...
# VisibilityMPH,Wind Direction,Wind SpeedMPH,Gust SpeedMPH,PrecipitationIn,...
# Events,Conditions,WindDirDegrees,DateUTC

data_weather = getCurrentWeather(locationName, now)
keyList = ['TimeLocal','TemperatureF','Dew PointF','Humidity','Sea Level PressureIn','VisibilityMPH','Wind Direction','Wind SpeedMPH','Gust SpeedMPH','PrecipitationIn','Events','Conditions','WindDirDegrees','DateUTC']
allDays_df = {keyList[i]: data_weather[i] for i in range(len(keyList))}

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
        return 'OK'
    else:
        return 'Dark'

allDays_df['Daylight']=daylightTest(allDays_df['TimeLocal'])

# Winds
def windTest(gust_speed):
    try:
        float(gust_speed)
    except ValueError:
        return 'NAN'
    else:
        if float(gust_speed)>20.0:
            return 'Gusty'
        else:
            return 'OK'

if allDays_df['Gust SpeedMPH'] == '-':
	allDays_df['Gust SpeedMPH'] == float(0.0)
allDays_df['Winds'] = windTest(allDays_df['Gust SpeedMPH'])

# Temperature
def tempTest(temp_F):
    try:
        float(temp_F)
    except ValueError:
        return 'NaN'
    else:
        if float(temp_F)<32.0:
            return 'Freezing Cold'
        elif float(temp_F)<50.0: #10C = 50F
            return 'Cold'
        else:
            return 'OK'

if allDays_df['TemperatureF'] == '':
	allDays_df['TemperatureF'] == 'NaN'
allDays_df['Temperature'] = tempTest(allDays_df['TemperatureF'])

# Clouds
def cloudTest(conditions):
    if conditions not in ['Clear', 'Scattered Clouds', 'Partly Cloudy', 'Sunny', 'Mostly Sunny', 'Few Clouds']:
        return 'Cloudy'
    else:
        return 'OK'

allDays_df['Clouds'] = cloudTest(allDays_df['Conditions'])

# Clean up missing values
# DO THIS FOR DICTIONARY
#allDays_df= allDays_df.replace('-9999', 'NaN')

# Jumpable Test
def jumpTest(all_tests):
    if all_tests['Daylight']=='OK' and all_tests['Winds']=='OK' and all_tests['Temperature']=='OK' and all_tests['Clouds']=='OK':
        return 'YES'
    else:
        return 'NO'

importantValues = {k: allDays_df[k] for k in ['Daylight', 'Winds', 'Temperature', 'Clouds']}
allDays_df['Jumpable'] = jumpTest(importantValues)

### Final Analysis

def finalPrint(outputConds):
    return outputConds['Daylight'] + ' ' + outputConds['Winds'] + ' ' + outputConds['Temperature'] + ' ' + outputConds['Clouds'] + ' ' + outputConds['Jumpable']

# THIS IS MESSY SYNTAX AND SLOPPY CODING
finalDict = {k: allDays_df[k] for k in ['Daylight', 'Winds', 'Temperature', 'Clouds', 'Jumpable']}
allDays_df['Finalout'] = finalPrint(finalDict)

timeofCheck = allDays_df['TimeLocal']
jumpingStatus = allDays_df['Finalout'][-1:]

if 'YES' in jumpingStatus:
    jumpingStatus = list(['Go Jumping!', 'YES'])
else:
    for element in jumpingStatus[:-1]:
        if element=='OK':
            jumpingStatus.remove(element)
    

# Output
# SLOPPY
print 'At ' + str(locationName) + ' as of ' + timeofCheck + ':'
print ' '.join(jumpingStatus[:-1])

#### ALL OF THE FOLLOWING IS OLD AND TO BE UPDATED ####
'''
# Daylight
def daylightTest(datetime_utc_string):

    format_utc_in = '%Y-%m-%d %H:%M:%S'
    
    # Do the test
    current_time=datetime.datetime.strptime(datetime_utc_string, format_utc_in)
        
    obs.date = current_time
    next_rise_time = obs.next_rising(sun).datetime()
    next_set_time = obs.next_setting(sun).datetime()
        
    # It's dark if the next sunrise is before the next sunset           
    if ( next_rise_time < next_set_time ):
        return 'Dark'
    else:
        return 'OK'

allDays_df['Daylight']=allDays_df['DateUTC'].apply( lambda x: daylightTest(x) )

# Winds
def windTest(gust_speed):
    try:
        float(gust_speed)
    except ValueError:
        return 'NAN'
    else:
        if float(gust_speed)>20.0:
            return 'Gusty'
        else:
            return 'OK'

allDays_df['Gust SpeedMPH']=allDays_df['Gust SpeedMPH'].map(lambda x: float(0.0) if x == '-' else x )
allDays_df['Winds'] = allDays_df['Gust SpeedMPH'].apply(lambda x: windTest(x) )

# Temperature
def tempTest(temp_F):
    try:
        float(temp_F)
    except ValueError:
        return 'NaN'
    else:
        if float(temp_F)<32.0:
            return 'Freezing Cold'
        elif float(temp_F)<50.0: #10C = 50F
            return 'Cold'
        else:
            return 'OK'

allDays_df['TemperatureF']=allDays_df['TemperatureF'].map(lambda x: 'NaN' if x == '' else x )
allDays_df['Temperature'] = allDays_df['TemperatureF'].apply(lambda x: tempTest(x) )

# Clouds
def cloudTest(conditions):
    if conditions not in ['Clear', 'Scattered Clouds', 'Partly Cloudy', 'Sunny', 'Mostly Sunny', 'Few Clouds']:
        return 'Cloudy'
    else:
        return 'OK'

allDays_df['Clouds'] = allDays_df['Conditions'].apply(lambda x: cloudTest(x) )

# Jumpable Test
def jumpTest(all_tests):
    if all_tests['Daylight']=='OK' and all_tests['Winds']=='OK' and all_tests['Temperature']=='OK' and all_tests['Clouds']=='OK':
        return 'YES'
    else:
        return 'NO'

allDays_df['Jumpable'] = allDays_df[['Daylight', 'Winds', 'Temperature', 'Clouds']].apply(jumpTest, axis=1) # pass object row-wise


# Make it an indexed Time Series, set as time zone aware
allDays_df=allDays_df.set_index('DateUTC')
allDays_df.index = pandas.to_datetime(allDays_df.index)
allDays_df_utc = allDays_df.tz_localize('UTC')

#allDays_df_utc.tz_convert('US/Eastern')

# Clean up missing values
allDays_df_utc = allDays_df_utc.replace('-9999', 'NaN')



### Final Analysis

def finalPrint(outputConds):
    return outputConds['Daylight'] + ' ' + outputConds['Winds'] + ' ' + outputConds['Temperature'] + ' ' + outputConds['Clouds'] + ' ' + outputConds['Jumpable']

allDays_df_utc['Finalout'] = allDays_df_utc[['Daylight', 'Winds', 'Temperature', 'Clouds', 'Jumpable']].apply(finalPrint, axis=1) # pass object row-wise

timeofCheck = str(allDays_df_utc['Finalout'][-1:].tz_convert(computerTZ).index.values).split(":00")[0].split("T")
jumpingStatus = allDays_df_utc['Finalout'][-1:].tz_convert(computerTZ)[-1].split()

if 'YES' in jumpingStatus:
    jumpingStatus = list(['Go Jumping!', 'YES'])
else:
    for element in jumpingStatus[:-1]:
        if element=='OK':
            jumpingStatus.remove(element)
    

# Output
print 'At ' + str(locationName) + ' as of: ' + timeofCheck[0].replace("['", "") + ' ' + timeofCheck[1]
print ' '.join(jumpingStatus[:-1])

'''
