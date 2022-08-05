
from datatable import dt, f, fread, as_type

raw_subjects = fread('~/Downloads/COSAS/cosasportal_patients.csv') 

raw_subjects = raw_subjects[f.UMCG_NUMBER!=None, :]

# pull variables of interest from portal table
subjects = raw_subjects[:, {
  'subjectID': f.UMCG_NUMBER,
  'belongsToFamily': f.FAMILIENUMMER,
  'belongsToMother': f.UMCG_MOEDER,
  'belongsToFather': f.UMCG_VADER,
  'belongsWithFamilyMembers': f.FAMILIELEDEN,
  'dateOfBirth': f.GEBOORTEDATUM,
  'yearOfBirth': None,
  'dateOfDeath': f.OVERLIJDENSDATUM,
  'yearOfDeath': None,
  'ageAtDeath': None,
  'genderAtBirth': f.GESLACHT,
  'ageAtDeath': None,
  'primaryOrganization': 'UMCG'
}][:, :, dt.sort(as_type(f.subjectID, int))]

# create a list of unique subject identifiers --- very important!!!!
cosasSubjectIdList = dt.unique(subjects['subjectID']).to_list()[0]

fetusData = subjects[f.FOETUS_ID != None, :]