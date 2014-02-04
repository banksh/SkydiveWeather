#!/usr/bin/python

import memcache

cache = memcache.Client(['127.0.0.1:11211'], debug=0)

def cacheExists(dz_name):
    return cache.get(dz_name)

def addToCache(dz_name,dz_data,timeout):
    cache.add(dz_name,dz_data,time=timeout)

def getData(dz_name):
    return cache.get(dz_name)
