import sys
import os
import re
import json
from os import listdir
from os.path import isfile, join

from xml.etree import ElementTree as ET
from io import StringIO
import urllib2

DEFAULT_DROPZONES_FILENAME = 'output/dropzones.json'
DEFAULT_OUTPUT_FILENAME = 'output/alldz_info.json'


def find_WOEID(dz_cityname, dz_zip):
    url = 'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20geo.places%20where%20text%3D%22{0}%20{1}%22&format=xml'.format(str(dz_cityname), str(dz_zip))
    xml = urllib2.urlopen(url).read()
    root = ET.XML(xml)
    
    woeid = root[0][0].find('{http://where.yahooapis.com/v1/schema.rng}woeid').text
    
    return woeid



if __name__ == "__main__":

    #Read
    input_filename = DEFAULT_DROPZONES_FILENAME
    data = []
    try:
        with open(input_filename, 'r') as f:
            for line in f:
                data.append(json.loads(line))
    except Exception as e:
        # Output a really annoying console message for each exception
        print('----- exception -----')
        print(e)
        print('----- /exception -----')
        pass
    finally:
        f.close()
    
    #Parse and output
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    else:
        output_filename = DEFAULT_OUTPUT_FILENAME

    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    output_file = open(output_filename, 'w')
    
    dz_count = 0
    dz_output = {}
    for dz in range(len(data)):
        dz_cityname, dz_zip = (data[dz]['address'][-1].split(',')[0], data[dz]['address'][-1].split()[-1])
        #Catches incomplete records
        if dz_cityname != dz_zip:
            try:
                woeid = find_WOEID(dz_cityname, dz_zip)
                if data[dz]['location_code'] != '':
                    dz_output['location_code']=data[dz]['location_code']
                    dz_output['name']=data[dz]['name']
                    dz_output['woeid']=woeid
                    output_file.write(json.dumps(dz_output) + os.linesep)
                    dz_count += 1
            except: continue
    output_file.close()
    
    
        
    print('Found ' + str(dz_count) + ' good dropzone records. Written to: ' + output_filename)
