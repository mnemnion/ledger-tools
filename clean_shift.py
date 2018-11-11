#!/usr/local/bin/python3
import sys
import re
file = sys.argv[1]
with open(file, 'r') as f:
    for line in f:
        print(re.sub(r'(\$[\d,]+)(?=[^"]*$)', lambda m: m.group(1).replace(',', ''), line), end = "")