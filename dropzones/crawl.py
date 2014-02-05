import os
import urllib2
import sys
from urlparse import urlparse

download_dir = 'pages'

if not os.path.exists(download_dir):
    os.makedirs(download_dir)

listing_file = open('listings.txt', 'r')
for line in listing_file:
    url_string = line.rstrip()

    url = urlparse(url_string)
    state = url.path.split('/')[3]

    page = urllib2.urlopen(url_string)

    print 'Downloading ' + state + ' listing page from url: ' + url_string
    output = open(os.path.join(download_dir, state + '.html'), 'wb')
    output.write(page.read())
    output.close()

print 'Finished downloading pages'
