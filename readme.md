# ledger-cli tools

This is a set of scripts I use to do personal accounting.

I don't like to account by hand, do most of my purchasing with a
card and wanted a (semi) automated way to sort through the CSVs
one can download from most banks.

If you bank with a credit union which uses cue-branch.com, you're
in luck, because I do as well. A converter is also provided for
Shift Payments, which will track both your USD price and the crypto
you sold for it.

The resulting ledger is in the order of the rows of the CSV, unless
it's reverse. To sort them use the creatively-named `date_sort.py`. Note
that it reads a limited subset of the ledger-cli language and tries
to do the right thing with lines it doesn't recognize; if you have a
use that breaks it, I'm interested, please file an issue.

The 'driver' is `accounts_map.json` This is a big Object, the keys
of which are accounts, and the values are either an Array or an
Array of Arrays, with two entries: the first is a regular expression
to search in the merchant description, the second (optional) is
something to call it.

Any merchant description which isn't recognized is bucketed into
"Expenses:Miscellaneous:Other", and the decription printed along with
the date and value.  It's about as easy to change the ledger entry as to
add to the JSON map so I tend to do the latter, making accounting easier
over time (with considerable spikes when I travel).

Sample CSVs are included for both formats. Pull requests with (anonymized)
samples of other formats are welcomed.

To extend, add a way to recognize the CSV by header(s) to `detect_csv_type`
then implement a function in the `extract(row)` family which returns a log.


### dependencies

uses `arrow` and `titlecase`, should work with Python 3 but I wouldn't know,
because no one pays me to maintain more than one python environment on my laptop and life is too short.



