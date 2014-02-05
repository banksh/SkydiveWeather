#!/bin/bash

virtualenv .
source bin/activate
pip install beautifulsoup4

echo
echo "===================================================="
echo "Run the following command to set up your virtualenv:"
echo
echo "                source bin/activate                 "
echo "===================================================="
echo

exit 0
