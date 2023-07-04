#//////////////////////////////////////////////////////////////////////////////
# FILE: files_new_data_prep.py
# AUTHOR: David Ruvolo
# CREATED: 2022-07-18
# MODIFIED: 2023-07-04
# PURPOSE: initial data processing
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#//////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis
from datatable import dt, f, fread, as_type
from dotenv import load_dotenv
from os import environ
from tqdm import tqdm
import pandas as pd
import re

# connect to cosas-db
load_dotenv()
host = environ['MOLGENIS_ACC_HOST']
cosas = Molgenis(host)
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

#//////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Processing and Import of Raw Data

# read data
portaldata = dt.rbind(
  # fread('~/Desktop/COSAS/COSAS.txt'),
  fread('~/Desktop/COSAS/FastQ_files_stored_prm05.txt'),
  fread('~/Desktop/COSAS/FastQ_files_stored_prm06.txt')
)


#///////////////////////////////////////

# ~ 🚨🚨🚨 ~ 
# RUN THIS STEP IF FASTQ file metadata is formatted incorrectly
# If applicable, fix dateCreated2 column. There are formatting issues with the
# received file that cause the last column (dateCreated2) to break onto a new
# line. Run a loop that identifies these rows and adds them to the previous row.

portaldata[:, dt.update(
  id=as_type(f.id, dt.Type.str32),
  dateCreated2 = as_type(f.dateCreated2, dt.Type.str32),
  keep = as_type(None, dt.Type.bool8)
)]

for index in tqdm(range(0, portaldata.nrows)):
  misplacedDate = portaldata[index, 'id']
  if misplacedDate:
    portaldata[index-1, 'dateCreated2'] = misplacedDate
    portaldata[index,'keep'] = False
    
portaldata = portaldata[f.keep!=False, :]
del portaldata['keep']

#///////////////////////////////////////

# 👌 continue
# drop uncessary columns only if they exist
for column in ['id', 'testID', 'md5']:
  if column in portaldata.names:
    print(f"Deleting column '{column}' from dataset....")
    del portaldata[column]


#///////////////////////////////////////

# ~ 🚨🚨🚨 ~ 
# run this step if you are working with FastQ metadata

# rename columns to make sure separated is read correctly
portaldata.names = {
  'fastQname1': 'fastQname_1',
  'fastQname2': 'fastQname_2',
  'dateCreated1': 'dateCreated_1',
  'dateCreated2': 'dateCreated_2'
}

# make sure dates are string otherwise the conversion will fail
portaldata[:, dt.update(
  dateCreated_1=as_type(f.dateCreated_1, dt.Type.str32),
  dateCreated_2=as_type(f.dateCreated_2, dt.Type.str32),
)]

portaldataDF = portaldata.to_pandas()

portaldataDF['_id'] = list(range(0, portaldata.nrows))
portaldataDF=pd.wide_to_long(
  df = portaldataDF,
  stubnames=['fastQname','md5', 'dateCreated'],
  sep='_',
  i='_id',
  j='x'
)

portaldata=dt.Frame(portaldataDF)
portaldata.names = {
  'fastQname': 'filename'
}

#///////////////////////////////////////

# 👌 CONTINUE

# NOTE: The following steps are applied to speed up the testing and development
# of the filemetadata script. Cases that do not meet the following criteria
# should be reviewed before including in the main job.

# remove rows where the umcgID does not meet the expected format
portaldata['hasValidUmcgId'] = dt.Frame([
  re.search(r'^([0-9]{2,})', d) and not re.search(r'^([0]{1,})$', d)
  for d in portaldata[:, f.umcgID].to_list()[0]
])


# remove rows where the dnaID does not meet the expected format
portaldata['hasValidDnaId'] = dt.Frame([
  bool(re.search(r'^(DNA[0-9]{2,})$', d)) if bool(d) else False
  for d in portaldata[:, f.dnaID].to_list()[0]
])

portaldata[:, dt.count(), dt.by(f.hasValidUmcgId)]
portaldata[:, dt.count(), dt.by(f.hasValidDnaId)]


# reduce data to valid umcg- and dna IDs only
portaldata = portaldata[(f.hasValidUmcgId) & (f.hasValidDnaId), :]
del portaldata[:, ['hasValidUmcgId', 'hasValidDnaId']]

#//////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Import data
cosas.importDatatableAsCsv('cosasportal_files', portaldata)
cosas.logout()
