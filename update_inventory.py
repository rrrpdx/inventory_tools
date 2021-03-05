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
	print("Usage: update_inventory <sheet>")
	print("          - This command will store the hashes, size, filename, root directory for all files under the current directory tree")
	print("          - The results will be stored to the <sheet> if it exists, or a new one will be created")

def md5(fname):
  hash_md5=hashlib.md5()
  with open(fname,"rb") as f:
    for chunk in iter(lambda: f.read(1024*1024),b""):
      hash_md5.update(chunk)
  return hash_md5.hexdigest()

if len(sys.argv)==1:
	usage()
	sys.exit()

count=0
dups=0
file_data={}
for root,dirs,files in os.walk('.'):
  for file in files:
    count=count+1
    if count%1000==0:
       print("Processing: "+str(count),file=sys.stderr)
    fname=root+'/'+file
    st=os.stat(fname)
    sz=st.st_size
    dir=root
    name=file
    csum=md5(fname)
    if csum in file_data:
        print("duplicate detected: "+name +' / ' +file_data[csum][1])
        dups=dups+1
    else:
      file_data[csum]=[sz,file,root]

n=pd.DataFrame.from_dict(file_data,orient='index',columns=['size','filename','directory'])

gc=pygsheets.authorize(client_secret=SECRET_FILE, credentials_directory=SECRET_DIRECTORY)
sheet=gc.open(GOOGLE_SHEETS_FILE)
#n=sheet.sheet1.get_as_df()
try: 
    worksheet=sheet.worksheet_by_title(sys.argv[1])
except:
    worksheet=sheet.add_worksheet(sys.argv[1],rows=10,cols=10)
worksheet.clear()

needed_cols=n.shape[1]+1
if needed_cols>worksheet.cols:
    worksheet.add_rows(needed_cols-worksheet.cols)

needed_rows=n.shape[0]+10
while worksheet.rows<needed_rows:
    print('Adding rows... Needed: '+str(needed_rows) + 'Current: '+str(worksheet.rows))
    worksheet.add_rows(10000)

worksheet.set_dataframe(n,'A1',copy_index=True)
print("Files Processed: "+str(count)+" Duplicates: "+str(dups))
