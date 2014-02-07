import json
import sys
import os
import re
import urllib2

#Format: "Recent %%% METAR history"

DEFAULT_INPUT_FILENAME = 'output/alldz_info.json'
DEFAULT_OUTPUT_FILENAME = 'output/alldz_info_fixed.json'

if len(sys.argv) > 1:
    output_filename = sys.argv[1]
else:
    output_filename = DEFAULT_OUTPUT_FILENAME

if not os.path.exists(os.path.dirname(output_filename)):
    os.makedirs(os.path.dirname(output_filename))

output_file = open(output_filename, 'w')

input_filename = DEFAULT_INPUT_FILENAME

input_file = open(input_filename, 'r')
json_data = json.load(input_file)

dz_count = 0
dz_output = {}

for item in json_data:

    current_location_code = item["location_code"]
    
    url = 'http://flightaware.com/resources/airport/{0}/weather'.format(str(current_location_code))
    try:
        page = urllib2.urlopen(url).read()
    
        found_string = re.findall("[A-Z]{3,4}\sTerminal\sArea", page)[0]

        dz_output['location_code']=found_string.split(" ")[0]
        dz_output['name']=item['name']
        dz_output['woeid']=item['woeid']
        output_file.write(json.dumps(dz_output) + os.linesep)
        dz_count += 1
    except:
        continue

input_file.close()
output_file.close()

print('Found ' + str(dz_count) + ' good dropzone records. Written to: ' + output_filename)
