import sys
import os
import re
import json
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

PAGES_DIR = 'pages'
DEFAULT_OUTPUT_FILENAME = 'output/dropzones.json'

REGION_REGEX = re.compile('^\s*USPA Region:\s*(.*)$')
LOCATION_REGEX = re.compile('^\s*Location:\s*(.*)$')
CODE_EXTRACTOR_REGEX = re.compile('^(.*)\s\((.*)\)$')

WHITESPACE_CLEANER_REGEX = re.compile('\s+')
PUNCTUATION_CLEANER_REGEX = re.compile('\s+([,\.])')
CONTACT_INFO_CLEANER_REGEX = re.compile('\sContact Information.*$')

def clean_text(text):
    cleaned_text = WHITESPACE_CLEANER_REGEX.sub(' ', text)
    cleaned_text = PUNCTUATION_CLEANER_REGEX.sub(r'\g<1>', cleaned_text)
    cleaned_text = CONTACT_INFO_CLEANER_REGEX.sub('', cleaned_text)
    return cleaned_text

def extract_code(text):
    try:
        matcher = CODE_EXTRACTOR_REGEX.match(text)
        return matcher.groups()
    except:
        return [text, '']

if __name__ == "__main__":
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    else:
        output_filename = DEFAULT_OUTPUT_FILENAME

    if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

    output_file = open(output_filename, 'w')

    try:
        dz_count = 0

        # Avoid getting directory listings
        file_listings = [ f for f in listdir(PAGES_DIR) if isfile(join(PAGES_DIR, f)) ]
        for file_listing in file_listings:
            f = open(join(PAGES_DIR, file_listing), 'r')

            try:
                # So beautiful!
                soup = BeautifulSoup(f.read())

                # Awkwardly finding the correct td
                dz_tds = soup.select('.ccontent')[1].select('table td[valign=middle]')

                for dz_td in dz_tds:
                    dz_record = {}

                    # If we got no real text, then skip this line
                    if len(dz_td.text.rstrip()) == 0:
                        continue

                    try:
                        dz_name = dz_td.select('span.subhead')[0].text

                        location_info = dz_td.select('div:nth-of-type(3)')
                        if len(location_info) == 1:
                            elements = location_info[0].text.split('\r\n')
                            first_element_splits = elements[0].split('\n')

                            region_line = REGION_REGEX.findall(first_element_splits[-2])[0]
                            region, region_code = extract_code(region_line)

                            location_line = LOCATION_REGEX.findall(first_element_splits[-1])[0]
                            location, location_code = extract_code(location_line)

                            address1 = clean_text(elements[1])
                            address2 = clean_text(elements[3])

                            dz_record['name'] = clean_text(dz_name)
                            dz_record['region'] = clean_text(region)
                            dz_record['region_code'] = clean_text(region_code)
                            dz_record['location'] = clean_text(location)
                            dz_record['location_code'] = clean_text(location_code)
                            dz_record['address'] = [x for x in [address1, address2] if x]

                            output_file.write(json.dumps(dz_record) + os.linesep)
                            dz_count += 1

                    except Exception as e:
                        # Output a really annoying console message for each exception
                        print('----- exception -----')
                        print(e)
                        print('----- /exception -----')
                        pass
            finally:
                f.close()
    except:
        output_file.close()

    print('Found ' + str(dz_count) + ' dropzones. Written to: ' + output_filename)
