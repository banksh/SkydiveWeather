#!/usr/bin/python

import dzdaemon, conditions, dzs, cgitb, cgi

cgitb.enable()
fs = cgi.FieldStorage()

dz_name = fs['airport'].value

if dzdaemon.cacheExists(dz_name):
    data = dzdaemon.getData(dz_name)
    debug = "Grabbed data from cache"
else: 
    data = conditions.getConditions(dz_name,dzs.IDs[dz_name])
    dzdaemon.addToCache(dz_name, data, timeout=3600)
    debug = "Had to update cache with data"

print "Content-type: text/plain"
print
print data, debug
