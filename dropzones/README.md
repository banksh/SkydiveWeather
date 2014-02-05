# Dropzone Data Collections

All instructions are relative to the folder in which this README.md is located.

## Initialize your environment

    $ [sudo] pip install virtualenv
    $ ./initialize.sh

Then do what the `initialize.sh` script tells you to!

## Crawl

    $ python crawl.py

Which then downloads into the `pages/` directory

## Parse Crawl Data

    $ python parse.py

Goes through the HTML files downloaded from the crawl and parses/sanitizes the data into the output file: `output/dropzones.json`

## JSON output file

The output file generated by the parser contains line-separated records of JSON objects. It should be read line-by-line, rather than as a whole (since it's not exactly valid JSON).