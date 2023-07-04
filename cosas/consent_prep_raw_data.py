#///////////////////////////////////////////////////////////////////////////////
# FILE: consent_prep_file.py
# AUTHOR: David Ruvolo
# CREATED: 2023-07-04
# MODIFIED: 2023-07-04
# PURPOSE: read xlsx file and import into the cosasportal
# STATUS: in.progess
# PACKAGES: **see below**
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from cosastools.molgenis import Molgenis
from os import environ, path, listdir
from datatable import dt, f, as_type
import pandas as pd


from dotenv import load_dotenv
load_dotenv()
cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

# read sheet
for file in listdir('../../Downloads'):
  if 'Inventarisatie' in file:
    filepath = path.abspath(f"../../Downloads/{file}")
    
consentDT = dt.Frame(pd.read_excel(filepath, sheet_name="5GPM snel diagnostiek", header=3))

consentDT.names = {
  'Analyse' : 'analysis',
  'Invoerdatum' : 'datefilled',
  'MDN/umcgnr' : 'MDN_umcgnr',
  'familienummer' : 'familienummer',
  'Anoniem gebruik van rest-lichaamsmateriaal voor het ontwikkelen van nieuwe of het .verbeteren van bestaande technieken' : 'request_consent_material',
  'labformulier en versie' : 'request_form',
  'Datum getekend' : 'request_date_signed',
  'Hercontact in de toekomst' : 'consent_recontact',
  'Diagnostiek in ontwikkeling': 'consent_diagnostics',
  'Wetenschappelijk onderzoek' : 'consent_research',
  'Systeem (Adlas, EPD)' : 'consent_system',
  'labformulier en versie.1' : 'consent_form',
  'toestemming niet aangevinkt, wel in brief van toegewezen arts terug te vinden' : 'consent_doctor',
  'Datum getekend.1' : 'consent_date_signed',
  'Informatie folder' : 'consent_folder',
  'Melden van "incidental findings"' : 'incidental_consent_recontact',
  'labformulier en versie.2' : 'incidental_form',
  'Datum getekend.2' : 'incidental_date_signed',
}

# set date columns
consentDT[:, dt.update(
  datefilled=as_type(f.datefilled, dt.Type.date32),
  incidental_date_signed=as_type(f.incidental_date_signed, dt.Type.date32),
  request_date_signed=as_type(f.request_date_signed, dt.Type.date32),
  consent_date_signed=as_type(f.consent_date_signed, dt.Type.date32)
)]

# import
cosas.delete('cosasportal_consent')
cosas.importDatatableAsCsv('cosasportal_consent',consentDT)