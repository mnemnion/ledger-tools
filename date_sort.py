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

entry = [""]

# This is an exceptionally dirty hack:
entries[arrow.get("0001-01-01")] = entry
# Please do not use this script on ledgers which predate the birth of Christ

count_in = 0

def date_pull(line):
   """Do our best to decipher a date"""
   try:
      date = arrow.get(line)
   except arrow.parser.ParserError:
      print("not a date: " + line)
      exit()
   return date

def append_entry(entry, date, line):
   """Append to existing date or add new entry"""
   if date in entries:
         entries[date].append(line)
   else: # New entry
      entry = [line]
      entries[date] = entry
   return entry

# Main event

# Parse the dates out and add to entries dict
for line in ledger:
   if digit.match(line):
      date = date_pull(line)
      entry = append_entry(entry, date, line)
   elif line[0] == ' ' or line[0] == '\n':
      entry.append(line)
   elif line[0] == 'P':
      date = date_pull(line[2:])
      entry = append_entry(entry, date, line)
   else:
      entry.append(line)

with out_ledger as out:
   for date in sorted(entries):
      for line in entries[date]:
         out.write(line)

















