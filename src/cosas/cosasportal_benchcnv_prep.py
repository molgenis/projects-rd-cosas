#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosasportal_benchcnv_prep.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-21
#' MODIFIED: 2022-02-21
#' PURPOSE: prep bench cnv dataset before mapping
#' STATUS: in.progress
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from src.python.utils_cosas import Molgenis, status_msg
from datatable import dt, f
from dotenv import load_dotenv
from os import environ
import numpy as np
import re

load_dotenv()
host=environ['MOLGENIS_HOST_ACC']
token=environ['MOLGENIS_TOKEN_ACC']


# ~ 0 ~
# Fetch Data
# Create connection to molgenis instance and pull benchcnv data from the portal
db = Molgenis(url=host, token=token)
benchcnvRaw = dt.Frame(
    db.get('cosasportal_benchcnv',batch_size=10000)
)

del benchcnvRaw['_href']

#//////////////////////////////////////

# ~ 1 ~ 
# Apply Transformations
#

# ~ 1a ~
# rename columns
benchcnv = benchcnvRaw[:,
    {
        'primid': f.primid,
        'belongsToFamily': f.secid,
        'observedPhenotype': f.phenotype
    }
]


# ~ 1b ~ 
# Identify cases to keep
# All records must have a valid ID (i.e., start with a number) and must contain
# at least one valid HPO code.
benchcnv['keep'] = dt.Frame([
    (
        bool(re.search(r'^[0-9].*', str(d[0]).strip())) and
        bool(re.search(r'^(HP:)', d[1].strip()))
    )
    for d in benchcnv[:, (f.primid, f.observedPhenotype)].to_tuples()
])

benchcnv = benchcnv[f.keep, :]
del benchcnv['keep']

# ~ 1c ~
# Format HPO codes
benchcnv['observedPhenotype'] = dt.Frame([
    ','.join(list(set(d.strip().split())))
    for d in benchcnv['observedPhenotype'].to_list()[0]
])


# ~ 1D ~
# Detect if subjectID is a fetus
benchcnv['isFetus'] = dt.Frame([
    'f' in d.lower()
    for d in benchcnv['primid'].to_list()[0]
])

# check for duplicate entries
if len(list(set(benchcnv['primid'].to_list()[0]))) != benchcnv.nrows:
    print(
        'Total number of distinct identifiers ({}) must match row numbers ({})'
        .format(
            len(list(set(benchcnv['primid'].to_list()[0]))),
            benchcnv.nrows
        )
    )


# ~ 1e ~
# Based on fetal status, compute other identifers
benchcnv = benchcnv.to_pandas().replace({np.nan: None}).to_dict('records')
for index,row in enumerate(benchcnv):
    value = row.get('primid').strip().replace(' ', '')
    if row['isFetus']:

        # Pattern 1: 99999F, 99999F1, 99999F1.2
        pattern1 = re.search(r'((F)|(F[-_])|(F[0-9]{,2})|(F[0-9]{1,2}.[0-9]{1,2}))$', value)
        
        # Patern 2: 99999F-88888, 99999_88888
        pattern2 = re.search(r'^([0-9]{1,}(F)?([0-9]{1,2})?[-_=][0-9]{1,})$', value)
        if pattern1:
            row['belongsToMother'] = pattern1.string.replace(pattern1.group(0),'')
            row['subjectID'] = pattern1.string
        elif pattern2:
            ids = re.split(r'[-_=]', pattern2.string)
            row['belongsToMother'] = ids[0].replace('F', '')
            row['subjectID'] = ids[0] #.replace('F', '')
            row['alternativeIdentifiers'] = ids[1]
        else:
            status_msg('{}. F detected in {}, but pattern is unexpected'.format(index, value))

#//////////////////////////////////////
#     
# ~ 2 ~
# Import into COSAS

# import prepped data
db.importData(entity = 'cosasportal_benchcnv_prepped', data = benchcnv)


# update identifiers in source table
importedIDs = [x['primid'] for x in benchcnv]
benchcnvRaw['processed'] = dt.Frame([
    d in importedIDs
    for d in benchcnvRaw['primid'].to_list()[0]
])

# sum(updatedIDs['processed'].to_list()[0])

cosasportal_benchcnv = (
    benchcnvRaw
    .to_pandas()
    .replace({np.nan: None})
    .to_dict('records')
)
db.updateData(entity = 'cosasportal_benchcnv', data=cosasportal_benchcnv)

# db.delete('cosasportal_benchcnv_prepped')
# db.delete('cosasportal_benchcnv')