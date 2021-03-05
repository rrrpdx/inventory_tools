#!/usr/bin/python3.6
import pygsheets
import sys
import os
import hashlib
import pandas as pd

SECRET_FILE='credentials.json'
SECRET_DIRECTORY='/home/rrrao/.google'
GOOGLE_SHEETS_FILE='archive_inventory'

def usage():
	print("Usage: update_inventory <sheet1> <sheet2>")
	print("          - This command will store the hashes, size, filename, root directory for all files under the current directory tree")
	print("          - The results will be stored to the <sheet> if it exists, or a new one will be created")


if len(sys.argv)!=3:
	usage()
	sys.exit()

gc=pygsheets.authorize(client_secret=SECRET_FILE, credentials_directory=SECRET_DIRECTORY)
sheet=gc.open(GOOGLE_SHEETS_FILE)

try: 
    worksheet1=sheet.worksheet_by_title(sys.argv[1])
except:
    print('Error: '+sys.argv[1]+' non found');
    sys.exit()

try: 
    worksheet2=sheet.worksheet_by_title(sys.argv[2])
except:
    print('Error: '+sys.argv[2]+' non found');
    sys.exit()



tbl1=worksheet1.get_as_df()
tbl2=worksheet2.get_as_df()

tbl1.set_index('hash',inplace=True)
tbl2.set_index('hash',inplace=True)

print(tbl1.loc[tbl1.index.difference(tbl2.index)])