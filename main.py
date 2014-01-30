import urllib2,datetime

# KORE
locationName='KORE'
#obs.lat = '42.57' #+N
#obs.long= '-72.2885' #+E
#utc_zone = tz.gettz('UTC')
#local_zone = tz.gettz('America/New_York')
#timeKey_options = ["TimeEST", "TimeEDT"]
locationID = 2465890 #FYI this is Orange, California



# Get today's date
now = datetime.datetime.now()

####### Today's Weather ####### 
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
		data_weather = [{s[0]:s[1:]} for s in data]
	return data_weather[-1]


####### SUNRISE AND SUNSET ####### 
# Get sunrise and sunset times
#l=2465890;curl -s |sed -n 's/.*sunrise="\([0-9:]\{1,\}\).*="\([0-9:]\{1,\}\).*/\1 \2/p'

def getSunriseSunset(loctionID):
	url_astro = "http://weather.yahooapis.com/forecastrss?w=" + str(locationID)
	try: 
		u_a = urllib2.urlopen(url_astro)
	except urllib2.URLError:
		end()
	else:
		data = u_a.read().split('<br />')
		data_astro = [s.strip('\n').split('\n') for s in data]

	#Returns a list of two strings, ['<sunrise>','<sunset>']
	return [i.strip(' am') if ' am' in i else ':'.join([str(int(str(i).strip(' pm').split(':')[0])+12),str(i).strip(' pm').split(':')[1]]) for i in str([i for i in data_astro[0] if i.startswith('<yweather:astronomy')]).split('"')[1::2]]	

exit()

######################## PROCESSING ########################
# Daylight
