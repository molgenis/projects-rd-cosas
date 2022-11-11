#///////////////////////////////////////////////////////////////////////////////
# FILE: cosas_consent.py
# AUTHOR: David Ruvolo
# CREATED: 2022-11-10
# MODIFIED: 2022-11-10
# PURPOSE: mapping script for consent dataset
# STATUS: in.progress
# PACKAGES: see below
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosas.api.molgenis2 import Molgenis
from dotenv import load_dotenv
from datatable import dt, f
from datetime import datetime
from os import environ
import pandas as pd
import re
load_dotenv()

def uniqueValuesById(data, groupby, column, dropDuplicates=True, keyGroupBy=True):
  """Unique Values By Id
  For a datatable object, collapse all unique values by ID into a comma
  separated string.

  @param data datatable object
  @param groupby name of the column that will serve as the grouping variable
  @param column name of the column that contains the values to collapse
  @param dropDuplicates If True, all duplicate rows will be removed
  @param keyGroupBy If True, returned object will be keyed using the value named in groupby
  
  @param datatable object
  """
  df = data.to_pandas()
  df[column] = df.dropna(subset=[column]) \
    .groupby(groupby)[column] \
    .transform(lambda val: ','.join(set(val)))
  if dropDuplicates:
    df = df[[groupby, column]].drop_duplicates()
  output = dt.Frame(df)
  if keyGroupBy:
    output.key = groupby
  return output


# connect to database
cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# pull list of existing patients
subjectIDs = dt.Frame(
  cosas.get(
    entity = 'umdm_subjects',
    attributes='subjectID'
  )
)['subjectID'].to_list()[0]

# pull raw data
data = dt.Frame(cosas.get('cosasportal_consent'))
del data[:, ['_href', 'id', 'analysis', 'datefilled']]

# trim all columns
for column in data.names:
  print('Trimming',f"data${column}")
  data[column] = dt.Frame([
    value.strip() if value is not None else value
    for value in data[column].to_list()[0]
  ])

consent = data.copy()

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Clean Consent Data

dt.unique(consent['MDN_umcgnr'])
consent[:, dt.count(), dt.by(f.MDN_umcgnr)][f.count > 1, :]

# reformat patient identifier
consent['MDN_umcgnr'] = dt.Frame([
  id.replace('.', '')
  for id in consent['MDN_umcgnr'].to_list()[0]
])

# ~ 1a ~
# recode request_consent_material
consentCategories = dt.unique(consent['request_consent_material'])
consentCategories['mapping'] = dt.Frame([
  True if value in ['wel bezwaar', 'bezwaar'] else (
    False if bool(re.search(r'^(geen bezwaa)', value)) else None
  )
  for value in consentCategories['request_consent_material'].to_list()[0]
])

consent['allowUseOfMaterial'] = dt.Frame([
  True if value in ['wel bezwaar', 'bezwaar'] else (
    False if not bool(re.search('^(geen bezwaar)', value)) else None
  )  
  for value in consent['request_consent_material'].to_list()[0]
])


# ~ 1b ~
# recode consent_recontact
recontactCategories = dt.unique(consent['consent_recontact'])
recontactCategories['mapping'] = dt.Frame([
  (
    True if value in ['wel'] else (
      False if value in ['niet'] else None
    )
  ) if value is not None else None
  for value in recontactCategories['consent_recontact'].to_list()[0]
])

consent['allowRecontacting'] = dt.Frame([
  (
    True if value in ['wel'] else (
      False if value in ['niet'] else None
    )
  ) if value is not None else None
  for value in consent['consent_recontact'].to_list()[0]
])

# ~ 1c ~
# recode research
researchCategories = dt.unique(consent['consent_research'])
researchCategories['mappings'] = dt.Frame([
  (
    True if bool(re.search(r'^(wel)', value)) else (
      False if value in ['niet'] else None
    )
  ) if value is not None else None
  for value in researchCategories['consent_research'].to_list()[0]
])

consent['allowGeneralResearchUse'] = dt.Frame([
  (
    True if bool(re.search(r'^(wel)', value)) else (
      False if value in ['niet'] else None
    )
  ) if value is not None else None
  for value in consent['consent_research'].to_list()[0]
])

# ~ 1d ~
# recode incidental findings
incidentalCategories = dt.unique(consent['incidental_consent_recontact'])
incidentalCategories['mappings'] = dt.Frame([
  (
    True if bool(re.search(r'^((w|W)el)', value)) else (
      False if bool(re.search(r'^(niet)', value)) else None
    )
  ) if value is not None else None
  for value in incidentalCategories['incidental_consent_recontact'].to_list()[0]
])

consent['allowRecontactingForIncidentalFindings'] = dt.Frame([
  (
    True if bool(re.search(r'^((w|W)el)', value)) else (
      False if bool(re.search(r'^(niet)', value)) else None
    )
  ) if value is not None else None
  for value in consent['incidental_consent_recontact'].to_list()[0]
])

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Build Datasets

# ~ 2a ~
# build: consents signed table --- stack attributes by form type
collectedBy='geneticadiagnostiek'

signedConsents = dt.rbind(
  consent[:, {
    'consentID': f.MDN_umcgnr,
    'consentFormType': 'aanvraagforumulier',
    'consentFormUsed': f.request_form,
    'dateFormSigned': f.request_date_signed,
    'collectedBy':  collectedBy
  }],
  consent[:, {
    'consentID': f.MDN_umcgnr,
    'consentFormType': 'toestemmingsforumlier',
    'consentFormUsed': f.consent_form,
    'dateFormSigned': f.consent_date_signed,
    'collectedBy':  collectedBy,
    'system': f.consent_system
  }],
  consent[:, {
    'consentID': f.MDN_umcgnr,
    'consentFormType': 'melden van incidental findings',
    'consentFormUsed': f.incidental_form,
    'dateFormSigned': f.incidental_date_signed,
    'collectedBy':  collectedBy
  }],
  force = True
)

# recode consentFormUsed
# Set values that are characters to None
# dt.unique(signedConsents['consentFormUsed'])
signedConsents['consentFormUsed'] = dt.Frame([
  None if (value in ['/', '-', '?']) and (value is not None) else value
  for value in signedConsents['consentFormUsed'].to_list()[0]
])

#///////////////////////////////////////

# recode dateFormSigned
# the column `dateFormSigned` has a mix of date formats.

# first remove all non-date values (i.e., '-', '?', text, etc.)
dt.unique(signedConsents['dateFormSigned'])
signedConsents['dateFormSigned'] = dt.Frame([
  None if (value is not None) and (bool(re.search(r'^([?/-])', value))) else value
  for value in signedConsents['dateFormSigned'].to_list()[0]
])

# !-------------- THIS NEEDS INPUT -----------------!
# Recode character-separated strings (',' or '/')
# How should values that have one (or more) forward slash be handled?
# "2022-11-11 / 2022-11-12". Which date is it? For now, I'm taking the
# first date. It needs to be decided which date to take, but it should
# be corrected in the spreadshet.
signedConsents[dt.re.match(f.dateFormSigned, '.*/\s+.*'), :]
signedConsents[dt.re.match(f.dateFormSigned, '.*,\s+.*'), :]

signedConsents['dateFormSigned'] = dt.Frame([
  re.split(r'([,/]\s+|[()])', value)[0].strip() if value is not None else value
  for value in signedConsents['dateFormSigned'].to_list()[0]
])

# dt.unique(signedConsents['dateFormSigned']).to_list()[0]

# recode forwardslashes to dashes -- this allows us to reformat the dates
signedConsents['dateFormSigned'] = dt.Frame([
  value.replace('/', '-') if value is not None else value
  for value in signedConsents['dateFormSigned'].to_list()[0]
])

# I'm assuming that dates are in dd-mm-yyyy format. Make sure all values follow
# this format.
signedConsents[
  dt.re.match(f.dateFormSigned, r'^([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})$') == False,
  (f.consentID, f.consentFormType, f.dateFormSigned)
]

# recode case(s) that are formatted as: xx-xx-xxxx
signedConsents['dateFormSigned'] = dt.Frame([
  (
    None if not bool(re.search(r'^([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})$', value)) else value
  ) if value is not None else value
  for value in signedConsents['dateFormSigned'].to_list()[0]
])


# reformat dates to yyyy-mm-dd format
signedConsents['dateFormSigned'] = dt.Frame([
  datetime.strptime(value, '%d-%m-%Y').date().strftime('%Y-%m-%d')
  if value is not None else value
  for value in signedConsents['dateFormSigned'].to_list()[0]
])

# dt.unique(signedConsents['dateFormSigned'])

#///////////////////////////////////////

# recode system
# Set values taht are characters to None
# dt.unique(signedConsents['system'])
signedConsents['system'] = dt.Frame([
  None if (value in ['?']) and (value is not None) else value
  for value in signedConsents['system'].to_list()[0]
])

# set xref
signedConsents['belongsToSubject'] = dt.Frame([
  value if value in subjectIDs else None
  for value in signedConsents['consentID'].to_list()[0]
])

signedConsents[f.belongsToSubject!=None,:]
signedConsents[f.belongsToSubject!=None,(f.consentID, f.belongsToSubject)]


# update consentID
# Now that records are linked with the patients table, make sure each consentID
# is unique
dt.unique(signedConsents['consentID']).nrows == signedConsents.nrows

signedConsents['idCount'] = dt.Frame(
  signedConsents.to_pandas().groupby(['consentID']).cumcount()
)

# save original ID to link with permissions dataset
signedConsents['rowID'] = signedConsents['consentID']

# create new ID
signedConsents['consentID'] = dt.Frame([
  '.'.join(map(str, tuple))
  if tuple[1] > 0 else tuple[0]
  for tuple in signedConsents[:, (f.consentID, f.idCount)].to_tuples()
])

cosas.importDatatableAsCsv('umdm_signedconsents', signedConsents)

#///////////////////////////////////////////////////////////////////////////////

# ~ 2 ~
# Build consent Permissions

permissions = consent[:, (
  f.MDN_umcgnr,
  f.allowUseOfMaterial,
  f.allowRecontacting,
  f.allowGeneralResearchUse,
  f.allowRecontactingForIncidentalFindings
)]

# collapse consent IDs so that the tables can be linked
signedForms = uniqueValuesById(
  data = signedConsents[:, (f.rowID, f.consentID)],
  groupby= 'rowID',
  column = 'consentID'  
)

signedForms.names = {'rowID': 'MDN_umcgnr', 'consentID': 'signedForms'}
permissions = permissions[:, :, dt.join(signedForms)]