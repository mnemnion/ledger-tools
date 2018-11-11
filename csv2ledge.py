#!/usr/local/bin/python

# CSV to Ledger converter, coopfcu and Shift Payments edition

import csv
import argparse
import arrow
import re
import json
import sys
from titlecase import titlecase
from collections import OrderedDict

ledger_file = sys.stdin
out_file = sys.stdout

entries = []
accounts = OrderedDict()

reverse_entries = True

MISC = 'Expenses:Miscellaneous:Other'
MAIN_ACCT = 'Assets:Checking'

UNITS = { "BTC" : "Assets:Bitcoin",
			 "ETH" : "Assets:Ethereum",
			 "LTC" : "Assets:Litecoin",
			 "BCH" : "SCAMCOINS:Bitcoin Cash"}

# Parse arguments

parser = argparse.ArgumentParser(description='Convert divers CSVs into Ledger format')

parser.add_argument('-i', '--in',
						  type=argparse.FileType('r'),
						  dest='infile',
						  help='CSV file to be converted')

parser.add_argument('-o', '--out',
						  type=argparse.FileType('w'),
						  help='ledger file (will overwrite!)')

args = parser.parse_args()

print args

if args.infile:
	ledger_file = args.infile

if args.out:
	out_file = args.out

# Take the JSON map and load the accounts as an ordered dict
# input JSON map:
# key: account category
# value:  a list  of [account regex, (account name)?]
# output OrderedDict:
# key: account regex
# val: tuple (account name | '', account category)
with open('./accounts_map.json', 'r') as accounts_file:
	account_json = json.load(accounts_file, object_pairs_hook=OrderedDict)
	for k,v in account_json.iteritems(): # key: account types
		if type(v) is list:
			if type(v[0]) is unicode:
				account_regex = re.compile(v[0])
				account_nick = ''
				if len(v) >= 2:
						account_nick = v[1]
				account_name = titlecase(account_nick)
				accounts[account_regex] = (account_name, k)
			elif type(v[0]) is list:
				for item in v:
					account_regex = re.compile(item[0])
					account_nick = ''
					if len(item) >= 2:
						account_nick = item[1]
					account_name = titlecase(account_nick)
					accounts[account_regex] = (account_name, k)
			else:
				raise ValueError('Badly formed JSON account value: ' + str(v))
		else:
			raise ValueError('Badly formed JSON account value' + str(v))


def detect_csv_type(csv_read):
	"""Attempt to automatically determine the CSV type and advance to the data if necessary.

	   If we can't, die."""
	first_row = csv_read.next()
	if first_row[0] == 'Transactions': # Shift Payments
		# clear the header
		csv_read.next()
		csv_read.next()
		csv_read.next()
		return 'shift'
	elif first_row[0] == 'Account Number': # New Coopfcu
		return 'coopfcu-new'
	elif first_row[0] == 'Date' and first_row[1] == 'Description':
		print 'Error: old coopfcu format, use commit b2b9c01af759ed912498c161d4e493b7ae32beb7'
		exit()
	elif first_row[1] == 'Time' and first_row[2] == 'TimeZone':
		return 'paypal'
	else:
		print 'Error, unrecognized CSV format: ' + repr(first_row)
		exit()

def str_minus(strnum):
	"""Take the minus of a string without conversion"""
	if strnum[0] == '-':
		return strnum[1:]
	else:
		return '-' + strnum

def extract_shift(row):

	categorized = False
	date = arrow.get(row[0], 'YYYY-MM-DD HH:mm:ss Z').format('YYYY-MM-DD HH:mm:ss')
	name = row[6]
	# Clean up the name a bit
	if name[-3:] == 'USA':
		name = name[:-5]
	amount_usd = row[1][1:]
	unit = row[3]
	amount_unit = str_minus(row[4])
	usd_per_unit = row[5]
	entry_type = MISC
	for k,v in accounts.iteritems():
		if k.search(name):
			if v[0] != '':
				name = v[0]
			entry_type = v[1]
			categorized = True
			break

	if not categorized:
		print(name + ' : ' + amount_usd + ' : ' + date)

	log = date + '   ' + 'Shift Payments' + '\n'
	log += '   ' + 'Assets:Cash' + '          $' +  amount_usd + '\n'
	log += '   ' + UNITS[unit] + '       ' + unit + ' ' + amount_unit + '{=' + usd_per_unit + '}\n'
	log += date + '   ' + titlecase(name) + '\n'
	log += '   ' + 'Assets:Cash' + '       $' +  str_minus(amount_usd) + '\n'
	log += '   ' + entry_type +  	'\n\n'

	return log


def extract_coopfcu(row):
	"""extract info from a coopfcu CSV row"""
	entry_date = arrow.get(row[2], 'MM/D/YYYY').format('YYYY-MM-DD')
	entry_description = row[5]
	entry_name = row[6]
	entry_amount = row[7] # would I need to convert? probably not.
	entry_type = MISC
	if entry_description == 'DEBIT CARD FEE':
		entry_type = 'Expenses:Coopfcu:Debit Card:Fee'
	elif entry_description == 'ATM FEE':
		entry_type = 'Expenses:Coopfcu:ATM:Fee'
		entry_name = 'ATM Fee (Coopfcu)'
	elif entry_description == 'ATM WITHDRAWAL':
		entry_type = 'Expenses:Coopfcu:ATM:Withdrawal'
		entry_name = 'ATM Withdrawal (Coopfcu)'
	elif entry_description == 'DIVIDEND':
		entry_type = 'Income:Dividend:Coopfcu'
		entry_name = 'Dividend (Coopfcu)'
	elif entry_description == 'SERVICE CHARGE':
		entry_type = 'Expenses:Coopfcu:Service Charge'
		entry_name = 'Service Charge (Coopfcu)'
	else:
		for k,v in accounts.iteritems():
			if k.search(entry_name):
				if v[0] != '':
					entry_name = v[0]
				entry_type = v[1]
				break
	if entry_name == row[6] and entry_type == MISC:
		print(entry_name + ' : ' + entry_amount)
	log = entry_date + '   ' + titlecase(entry_name) + '\n'
	log += '   ' + MAIN_ACCT + '       $' + entry_amount + '\n'
	log += '   ' + entry_type + '\n'
	return log

with ledger_file as csvfile:
	csv_read = csv.reader(csvfile)
	print 'Miscellaneous Entries:'
	csv_type = detect_csv_type(csv_read)
	if csv_type == 'coopfcu-new':
		extract = extract_coopfcu
	elif csv_type == 'shift':
		reverse_entries = False
		extract = extract_shift
	else:
		print 'CSV type ' + csv_type + ' not yet supported'
		exit()
	for row in csv_read:
		log = extract(row)
		if not log == '':
			entries.append(log)

with out_file as out:
	out.write(';; ~Auto Generated~ @ ' + arrow.now().format()
		      + ' from ' + args.infile.name + '\n\n')
	if reverse_entries:
		for entry in reversed(entries):
			out.write(entry)
	else:
		for entry in entries:
			out.write(entry)
		out.write(entry)