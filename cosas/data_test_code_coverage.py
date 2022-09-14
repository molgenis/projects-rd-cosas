
from dotenv import load_dotenv
from os import environ
from cosas.api.molgenis2 import Molgenis
from datatable import dt, f, fread

load_dotenv()
cosas = Molgenis(environ['MOLGENIS_ACC_HOST'])
cosas.login(environ['MOLGENIS_ACC_USR'], environ['MOLGENIS_ACC_PWD'])

currentLabCodes = dt.Frame(cosas.get('umdm_labProcedures'))
sourceLabCodes = fread('~/Downloads/COSAS/cosasportal_metadata.csv')


del currentLabCodes['_href']

sourceLabCodes['testCodeExistsInCosas'] = dt.Frame([
  code in currentLabCodes['code'].to_list()[0]
  for code in sourceLabCodes['TEST_CODE'].to_list()[0]
])

sourceLabCodes['testCodeExistsInCosas'] = sourceLabCodes[
  :, dt.as_type(f.testCodeExistsInCosas, dt.str32)
]

sourceLabCodes[:, dt.count(), dt.by(f.testCodeExistsInCosas)]

sourceLabCodes.to_csv('~/Downloads/cosasportal_metadata_cosas_checked.csv')