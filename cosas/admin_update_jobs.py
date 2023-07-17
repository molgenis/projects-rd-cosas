#///////////////////////////////////////////////////////////////////////////////
# FILE: admin_update_jobs.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-14
# MODIFIED: 2023-07-14
# PURPOSE: update scheduled jobs reporting table
# STATUS: in.progress
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis
from datatable import dt, f, as_type

# ~ local ~
from os import environ
from dotenv import load_dotenv
load_dotenv()
cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# ~ PROD ~
# cosas = Molgenis('http://localhost/api/', '${molgenisToken}')

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Retrieve metadata

# pull scheduled jobs
schedule = dt.Frame(
  cosas.get(
    'sys_job_ScheduledJob',
    attributes='name,description,cronExpression'
  )
)
del schedule['_href']

schedule.names = {'cronExpression':'cron'}
schedule[:, dt.update(
  dateLastRun=as_type(None, dt.Type.str32),
  isStable=as_type(None, dt.Type.str32)
)]

# pull history of runs
history = dt.Frame(
  cosas.get(
    'sys_job_ScriptJobExecution',
    attributes='name,status,submissionDate'
  )
)

del history['_href']

history['submissionDate'] = dt.Frame([
  value.split('T')[0] if bool(value) else value
  for value in history['submissionDate'].to_list()[0]
])

history[:, dt.update(
  submissionDate=as_type(f.submissionDate, dt.Type.date32)
)]


# map data by cron expression as names and labels differ
for job in schedule['cron'].to_list()[0]:
  # filter history to known job
  jobHistory = history[f.cron == job, :]
  
  if jobHistory.nrows:
  
    # find the most recent date and convert to date string and
    # set date class to string
    recentDate = jobHistory[:, f.submissionDate].max1().strftime('%Y-%m-%d')
    jobHistory[:, dt.update(submissionDate=as_type(f.submissionDate, dt.Type.str32))]
  
    # find most recent run
    recentRun = jobHistory[(f.name==job) & (f.submissionDate == recentDate), :]
    
    # update schedule dataset
    schedule[f.name==job,f.dateLastRun] = recentRun['submissionDate'].to_list()[0][0]
    schedule[f.name==job,f.isStable] = recentRun['status'].to_list()[0][0]
  
  else:
    schedule[f.name==job, f.dateLastRun] = None
    schedule[f.name==job, f.isStable] = 'INACTIVE'
    

dt.unique(history['name'])
schedule[:, ['name','cron','dateLastRun','isStable']]

# recode values
schedule['isStable'] = dt.Frame([
  value == 'SUCCESS'
  for value in schedule['isStable'].to_list()[0]
])


# cosas.importDatatableAsCsv('cosasreports_jobs', schedule)