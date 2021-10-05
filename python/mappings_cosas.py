#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosas.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-10-05
#' PURPOSE: primary mapping script for COSAS
#' STATUS: in.progress
#' PACKAGES: datatable
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


import pandas as pd
def read_xlsx(path, nrows = None, usecols = None, converters = None):
    data = pd.read_excel(
        path,
        engine = 'openpyxl',
        nrows = nrows,
        usecols = usecols,
        converters = converters,
        dtype = str
    )
    return data.to_dict('records')


import re
from datetime import datetime


def __format__date__(date: str, pattern = '%Y-%m-%d %H:%M:%S') -> str:
    """Format Date String
    
    Format date string to yyyy-mm-dd format
    
    @param string : date string
    @param pattern : date format, default: %Y-%m-%d %H:%M:%S
    
    @return date
    """
    if not date or pd.isna(date):
        return None
    
    return datetime.strptime(date, pattern).date()

def map_patients(data):
    """Map COSAS Patients
    
    Map portal data into `cosas_patients` structure.
    
    @param data : list of dictionaries (output from `cosasportal_patients`)
    
    @return a list of dictionaries shaped for `cosas_patients`
    """
    out = []
    for d in data:
        tmp = {
            'umcgID': int(d.get('UMCG_NUMBER')),
            'familyID': int(d.get('FAMILIENUMMER')),
            'dateOfBirth': __format__date__(date = d.get('GEBOORTEDATUM', None)),
            'biologicalSex': d.get('GESLACHT', None).lower(),
            'maternalID': d.get('UMCG_MOEDER', None),
            'paternalID': d.get('UMCG_VADER', None),
            'linkedFamilyIDs': re.sub(r'(\s+)?[,]\s+', ',', d.get('FAMILIELEDEN', None)),
            'dateOfDeath': __format__date__(date = d.get('OVERLIJDENSDATUM')),
            'inclusionStatus': 'alived'
        }
        
        # if deceased 
        if tmp['dateOfDeath']:
            tmp['inclusionStatus'] = 'deceased'
            tmp['ageAtDeath'] = tmp['dateOfDeath'] - tmp['dateOfBirth']
        
        # finalize dates for import into COSAS
        if tmp['dateOfBirth'] is not None: str(tmp['dateOfBirth'])
        if tmp['dateOfDeath'] is not None: str(tmp['dateOfDeath'])
        out.append(tmp)
    
    return sorted(out, key = lambda d: (d['umcgID']))
    

def map_clinical(data):
    """Map COSAS Clinical
    
    Map portal data into `cosas_clinical`. The purpose of this table is to
    present all phenotypic information. The structure of the data is in long
    format, but it needs to be in wide format. Using the phenotypic rating
    (niet zeker, zeker, onzeker, etc), we can develop provisional-, excluded-,
    and provisional phenotypes.
    
    @param data (list) : output from `cosasportal_diagnoses`
    
    @return list of dictionaries prepped for `cosas_clincial`
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # COLLAPSE COLUMNS
    # collapse diagnosis columns so that primary and extract diagnoses are in
    # a single column. Remove blank rows and standardize codes.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    rawDiagnoses = []
    for d in data: 
        
        # collapse columns per row
        dx = [{
            'umcgID': d.get('UMCG_NUMBER'),
            'diagnosis': d.get('HOOFDDIAGNOSE'),
            'certainty': d.get('HOOFDDIAGNOSE_ZEKERHEID').lower()
        },{
            'umcgID': d.get('UMCG_NUMBER'),
            'diagnosis': d.get('EXTRA_DIAGNOSE'),
            'certainty': d.get('EXTRA_DIAGNOSE_ZEKERHEID').lower(),
        }]
        
        # keep cases that aren't blank
        for el in dx:
            if el['diagnosis'] != '-':
                el['code'] = 'dx_' + re.sub(r'([\s:]+)', '', el['diagnosis'].split(':')[0])
                el['certainty'] = el['certainty'].replace(' ', '-')
                el.pop('diagnosis')
                rawDiagnoses.append(el)
        

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # CREATE TABLE STRUCTURE
    # In COSAS, we have created the columns for various levels of phenotypic
    # information (provisional, excluded, etc.). Each row is a patient and
    # all unique diagnostic codes per certainty level.
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    provChoices = ['zeker', 'niet-zeker', 'onzeker', None]
    diagnoses = []
    seen = []
    for d in rawDiagnoses:
        if d['umcgID'] not in seen:
            
            # prep new row
            patientDx = {
                'umcgID': d.get('umcgID'),
                'provisionalPhenotype': None,
                'excludedPhenotype': None
            }
            
            # find all patient records and create subsets by certainty rating
            result = list(filter(lambda x: x['umcgID'] in d['umcgID'], rawDiagnoses))
            provData = list(filter(lambda x: x['certainty'] in provChoices, result))
            exclData = list(filter(lambda x: x['certainty'] in 'zeker-niet', result))
            
            # collapse codes and keep only unique values
            if provData:
                patientDx['provisionalPhenotype'] = ','.join(
                    list(set( [x['code'] for x in provData] ))
                )
                
            if exclData:
                patientDx['excludedPhenotype'] = ','.join(
                    list(set( [x['code'] for x in exclData] ))
                )
            
            
            # append data
            diagnoses.append(patientDx)
            seen.append(d.get('umcgID'))
    
    return diagnoses
    

dx = read_xlsx(path = '_raw/cosasportal_diagnoses.xlsx')
diagnoses = map_clinical(dx)


# data = read_xlsx(path = '_raw/cosasportal_patients.xlsx')
# patients = map_patients(data)
# [print(p) for p in patients[:10]]