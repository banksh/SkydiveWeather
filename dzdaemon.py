#!/usr/bin/python

import memcache

cache = memcache.Client(['localhost:12121'],debug=0)

def cacheExists(dz_name):
    return cache.get(dz_name)

def addToCache(dz_name,dz_data,timeout):
    cache.add(dz_name,dz_data,time=timeout)

def getData(dz_name):
    return cache.get(dz_name)
