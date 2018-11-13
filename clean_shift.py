#!/usr/local/bin/python
"""Shift branch CSVs have commas in the dollar amounts.

Let's fix that."""
import sys
import re
file = sys.argv[1]
with open(file, 'r') as f:
    for line in f:
        print(re.sub(r'(\$[\d,]+)(?=[^"]*$)',
                    lambda m: m.group(1).replace(',', ''),
                    line), end = "")