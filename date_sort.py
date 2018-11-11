#!/usr/local/bin/python

"""Sort a ledger by date"""

import sys
import re
import argparse
import arrow


ledger = sys.stdin
out_ledger = sys.stdout

# Parse arguments

parser = argparse.ArgumentParser(description='Sort a ledger by date.')

parser.add_argument('-i', '--in',
                    type=argparse.FileType('r'),
                    dest='infile',
                    help='Ledger file to sort (default stdin)')

parser.add_argument('-o', '--out',
                    type=argparse.FileType('w'),
                    help='sorted ledger (default stdout)')

args = parser.parse_args()

if args.infile:
   ledger = args.infile

if args.out:
   out_ledger = args.out

# regex for digits

digit = re.compile(r'\d')

# Container for entries
# key: arrow date object, value: full text of entry
entries = {}

entry = None

count_in = 0

for line in ledger:
   if digit.match(line):
      # We should have a date
      date = None
      try:
         date = arrow.get(line, "YYYY-MM-DD HH:mm:ss")
      except arrow.parser.ParserError:
         try:
            date = arrow.get(line, "YYYY-MM-DD")
         except arrow.parser.ParserError:
            print("not a date: " + line)
            exit()
      # We might have an identical date, if so, append to that
      if date in entries:
         entries[date].append(line)
      else: # New entry
         entry = []
         entry.append(line)
         entries[date] = entry
   elif line[0] == ' ' or line[0] == '\n':
      if not entry:  # This happens if the first line is not a date
         entry = []
         # This is an exceptionally dirty hack:
         entries[arrow.get("0001-01-01")] = entry
         # Please do not use this script on ledgers which predate the birth of Christ
      entry.append(line)
   else:
      # This should handle commodity prices and other things with dates
      # in them, in the mean time it's a copyclone:
      if not entry:  # This happens if the first line is not a date
         entry = []
         # This is an exceptionally dirty hack:
         entries[arrow.get("0001-01-01")] = entry
         # Please do not use this script on ledgers which predate the birth of Christ
      entry.append(line)
   count_in += 1

count_out = 0

with out_ledger as out:
   for date in sorted(entries):
      for line in entries[date]:
         out.write(line)
         count_out +=1

if count_out != count_in:
   # This doesn't actually count writes, I need to go back in and
   # compare these manually

   print("Warning: line counts don't match! in: "
            + repr(count_in) + " out: " + repr(count_out))

















