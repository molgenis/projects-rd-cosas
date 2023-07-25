#///////////////////////////////////////////////////////////////////////////////
# FILE: cosasreports_jobs.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-25
# MODIFIED: 2023-07-25
# PURPOSE: update jobs table status
# STATUS: stable
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis
from datatable import dt, f, as_type

# ~ LOCAL ~
# from os import environ
# from dotenv import load_dotenv
# load_dotenv()
# cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# ~ PROD ~
cosas = Molgenis('http://localhost/api/', '${molgenisToken}')

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Retrieve data

# data sources
sourcesDT = dt.Frame(cosas.get('cosasreports_datasources'))
del sourcesDT['_href']

# get scheduled jobs
scheduleDT = dt.Frame(
  cosas.get(
    'sys_job_ScheduledJob',
    attributes='name,description,cronExpression,active'
  )
)
del scheduleDT['_href']

# init columns
scheduleDT[:, dt.update(
  dateLastRun = as_type(None, dt.Type.str32),
  isStable = as_type(None, dt.Type.str32)
)]

scheduleDT.names = {
  'cronExpression': 'cron',
  'active': 'isActive'
}


# get job execution history
historyDT = dt.Frame(
  cosas.get(
    'sys_job_ScriptJobExecution',
    attributes='name,status,submissionDate',
    q='submissionDate=ge=2023-07-01T00:00:00Z;name!=TEST'
  )
)

del historyDT['_href']

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Prepare data and merge job history

# Recode Data
# recode job history names to map to scheduled job names
mapping = {
  'DATABASE ADMIN: Clean up scripts': 'DATABASE: Clean up tokens',
  'VARIANTDB: Daily imports ADLAS variants': 'VariantDB: Daily import and update',
  'COSAS REPORTS: Generate Attribute Summary': 'COSAS: Generate Attribute Summary',
}

historyDT['name'] = dt.Frame([
  mapping[value] if value in mapping else value
  for value in historyDT['name'].to_list()[0]
])


# Change submissionDate to date
historyDT['submissionDate'] = dt.Frame([
  value.split('T')[0]
  for value in historyDT['submissionDate'].to_list()[0]
])

historyDT[:, dt.update(submissionDate=as_type(f.submissionDate, dt.Type.date32))]


# Merge status and date last run with scheduled jobs
for job in scheduleDT['name'].to_list()[0]:
  
  # isoloate job history and get the last date script was executed
  jobHistoryDT = historyDT[f.name == job, :]
  jobRecentDate = jobHistoryDT[:, dt.max(f.submissionDate)].to_list()[0][0].strftime('%Y-%m-%d')
  
  # get row containing the most recent job execution
  jobHistoryDT[:, dt.update(submissionDate=as_type(f.submissionDate, dt.Type.str32))]
  jobRecentRunDT = jobHistoryDT[(f.name == job) & (f.submissionDate==jobRecentDate), :]
  
  # update schedule table
  scheduleDT[f.name == job, (f.dateLastRun, f.isStable)] = jobRecentRunDT[
    :, (f.submissionDate, f.status)
  ].to_tuples()[0]
  


# Recode `isStable` values to bool and convert to string for import
scheduleDT['isStable'] = dt.Frame([
  value == 'SUCCESS' for value in scheduleDT['isStable'].to_list()[0]
])


#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Update Data Sources
# For all jobs, update the data sources table to indicate if there is an issue
# in the overall workflow

# set cosas sources: Adlas and Darwin
cosasJobsDT = scheduleDT[dt.re.match(f.name, 'COSAS.*'), ['isActive','isStable']]
for row in cosasJobsDT.to_tuples():
  if (row[0] is False) or (row[1] is False):
    sourcesDT[dt.re.match(f.source, 'ADLAS|Darwin'),'status'] = -1


# set alissa sources
alissaJobsDT = scheduleDT[dt.re.match(f.name, 'Alissa.*'), ['isActive','isStable']]
for row in alissaJobsDT.to_tuples():
  if (row[0] is False) or (row[1] is False):
    sourcesDT[dt.re.match(f.source, 'Alissa'), 'status'] = -1
    
    
# set cartagenia source
cartageniaJobDT = scheduleDT[dt.re.match(f.name, 'Cartagenia.*'), ['isActive','isStable']]
for row in cartageniaJobDT.to_tuples():
  if (row[0] is False) or (row[1] is False):
    sourcesDT[dt.re.match(f.source, 'Cartagenia.*'), 'status'] = -1
    
    
# set consent source status
consentJobDT = scheduleDT[dt.re.match(f.name, 'Consent.*'), ['isActive','isStable']]
for row in consentJobDT.to_tuples():
  if (row[0] is False) or (row[1] is False): 
    sourcesDT[f.source=='Consent Files', 'status'] = -1
  

# set file metadata processing status
filesJobDT = scheduleDT[dt.re.match(f.name,'.*Daily file.*'), ['isActive', 'isStable']]
for row in filesJobDT.to_tuples():
  if (row[0] is False) or (row[1] is False):
    sourcesDT[dt.re.match(f.source,'Analyis.*'), 'status'] = -1

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Import

# last preparations
scheduleDT[:, dt.update(
  isStable=as_type(f.isStable, dt.Type.str32),
  isActive=as_type(f.isActive, dt.Type.str32)
)]


cosas.importDatatableAsCsv('cosasreports_datasources', sourcesDT)
cosas.importDatatableAsCsv('cosasreports_jobs', scheduleDT)

cosas.logout()
