#///////////////////////////////////////////////////////////////////////////////
# FILE: cosas_consent.py
# AUTHOR: David Ruvolo
# CREATED: 2022-11-10
# MODIFIED: 2023-07-04
# PURPOSE: mapping script for consent dataset
# STATUS: stable
# PACKAGES: see below
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis,print2
from cosastools.datatable import uniqueValuesById
from datatable import dt, f
import re

print2('Running: Cosas consent mapping script....')

# connect: dev
# from dotenv import load_dotenv
# from os import environ
# import re
# load_dotenv()
# cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
# cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# connect: prod
cosas = Molgenis('http://localhost/api/', '${molgenisToken}')

#///////////////////////////////////////////////////////////////////////////////

# ~ 0 ~
# Retrieve data and transform

print2('Retrieving COSAS metadata and raw consent data...')

# get existing subject IDs
subjects = cosas.get('umdm_subjects', attributes='subjectID', batch_size=10000)
subjectIDs = dt.Frame(subjects)['subjectID'].to_list()[0]


# get consent data
consentraw = dt.Frame(cosas.get('cosasportal_consent'))
del consentraw[:, ['_href', 'id', 'analysis', 'datefilled']]


# trim all columns
for column in consentraw.names:
  consentraw[column] = dt.Frame([
    value.strip() if value is not None else value
    for value in consentraw[column].to_list()[0]
  ])

consent = consentraw.copy()

#///////////////////////////////////////////////////////////////////////////////

# ~ 1 ~
# Clean Consent Data

# ~ 1a ~
# reformat patient identifier: take out separator ('.')
consent['MDN_umcgnr'] = dt.Frame([
  id.replace('.', '') for id in consent['MDN_umcgnr'].to_list()[0]
])


# ~ 1b ~
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


# ~ 1c ~
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


# ~ 1d ~
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


# ~ 1e ~
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

# ~ 1f ~
# recode diagnostic use
diagnosticCategories = dt.unique(consent['consent_diagnostics'])
diagnosticCategories['mappings'] = dt.Frame([
  (
    True if bool(re.search(r'^((w|W)el)', value)) else (
      False if bool(re.search(r'^(niet)', value)) else None
    )
  ) if value is not None else None
  for value in diagnosticCategories['consent_diagnostics'].to_list()[0]
])

consent['allowDiagnosticUse'] = dt.Frame([
  (
    True if bool(re.search(r'^((w|W)el)', value)) else (
      False if bool(re.search(r'^(niet)', value)) else None
    )
  ) if value is not None else None
  for value in consent['consent_diagnostics'].to_list()[0]
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

#///////////////////////////////////////

# ~ 2b ~
# recode consentFormUsed
# Set values that are characters to None
signedConsents['consentFormUsed'] = dt.Frame([
  None if (value in ['/', '-', '?']) and (value is not None) else value
  for value in signedConsents['consentFormUsed'].to_list()[0]
])

#///////////////////////////////////////

# ~ 2c ~
# recode dateFormSigned
# the column `dateFormSigned` has a mix of date formats.

# first remove all non-date values (i.e., '-', '?', text, etc.)
signedConsents['dateFormSigned'] = dt.Frame([
  value.split('00:')[0].strip() if value else value
  for value in signedConsents['dateFormSigned'].to_list()[0]
])

#///////////////////////////////////////

# ~ 2d ~
# recode system
# Set values that are characters to None
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


#///////////////////////////////////////

# ~ 2e ~
# update consentID
# Now that records are linked with the patients table, make sure each consentID
# is unique

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

#///////////////////////////////////////////////////////////////////////////////

# ~ 3 ~
# Build consent Permissions

# select columns of interest
permissions = consent[:, (
  f.MDN_umcgnr,
  f.allowUseOfMaterial,
  f.allowRecontacting,
  f.allowGeneralResearchUse,
  f.allowRecontactingForIncidentalFindings,
  f.allowDiagnosticUse
)]


# collapse all signed forms IDs to link tables
signedForms = uniqueValuesById(
  data = signedConsents[:, (f.rowID, f.consentID)],
  groupby= 'rowID',
  column = 'consentID'  
)


signedForms.names = {'rowID': 'MDN_umcgnr', 'consentID': 'signedForms'}
permissions = permissions[:, :, dt.join(signedForms)]
permissions.names = { 'MDN_umcgnr': 'consentID' }

# select distinct records only
permissions = permissions[:, dt.first(f[:]), dt.by(f.consentID, f.signedForms)]


# create link between the permissions and patients tables
permissions['belongsToSubject'] = dt.Frame([
  value if value in subjectIDs else None
  for value in permissions['consentID'].to_list()[0]
])

#///////////////////////////////////////
  
# ~ 4 ~
# import
cosas.importDatatableAsCsv('umdm_signedconsents', signedConsents)
cosas.importDatatableAsCsv('umdm_consent', permissions)
cosas.logout()
