#!/usr/bin/python

import dzdaemon, conditions, dzs, cgitb, cgi, re, json

cgitb.enable()
fs = cgi.FieldStorage()

try: dz_name = str(fs['airport'].value)
except: dz_name = 'error'

if not re.match("^[a-zA-Z]+$", dz_name): dz_name = 'error'

try:
    if dzdaemon.cacheExists(dz_name):
        data = dzdaemon.getData(dz_name)
        debug = "Grabbed data from cache"
    else: 
        json_file = open('../../alldz_info.json')
        json_data = json.load(json_file)
        for item in json_data:
            if item["location_code"] == "61C":
                woeid = item["woeid"]
        data = conditions.getConditions(dz_name,woeid)
        dzdaemon.addToCache(dz_name, data, timeout=3600)
        debug = "Had to update cache with data"
    
    output = {'Jumpable':data['Jumpable']}
    del data['Jumpable']
    output['Conditions'] = '</br>'.join(["%s: %s"%(key,data[key]) for key in data])
    print "Content-type: text/json"
    print
    print json.dumps(output)
    #print '</br>'.join(["%s: %s"%(key,data[key]) for key in data]), "</br></br>", debug

except KeyError:
    print "Content-type: text/plain"
    print
    print "Invalid METAR location"

