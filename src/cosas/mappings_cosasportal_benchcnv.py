#'////////////////////////////////////////////////////////////////////////////
#' FILE: mappings_cosasportal_benchcnv.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-17
#' MODIFIED: 2022-02-17
#' PURPOSE: process Cartegenia data for use in cosas_mappings
#' STATUS: in.progress
#' PACKAGES: molgenis.client, datatable
#' COMMENTS: This script is designed to be run outside of molgenis
#'////////////////////////////////////////////////////////////////////////////

from datatable import dt, f, as_type, first
from src.cosas.cosas_mappings import Molgenis

db = Molgenis(url='http://localhost/api/', token='${molgenisToken}')

# pull raw data
clinicalData = dt.Frame(
    db.get(
        entity = 'cosasportal_benchcnv',
        batch_size=10000,
        attributes = 'primid,Phenotype'
    )
)

# rename columns
clinicalData = clinicalData[
    :, {
        'clinicalID': f.primid,
        'observedPhenotye': f.Phenotype
    }
]


# format `Phenotype`
clinicalData['observedPhenotye'] = dt.Frame([
    ','.join(list(set(d.strip().split())))
    for d in clinicalData['observedPhenotye'].to_list()[0]
])







#//////////////////////////////////////////////////////////////////////////////

# EXTRA CODE
# not sure if I want to remove it just yet

# maternalIDs = subjects[
#     f.belongsToMother != None, f.belongsToMother
# ][
#     :, first(f[:]), dt.by(f.belongsToMother)
# ].to_list()[0]

# familyIDs = subjects[
#     f.belongsToFamily != None, f.belongsToFamily
# ][
#     :, first(f[:1]), dt.by(f.belongsToFamily)
# ].to_list()[0]


# clinicalDF = raw_bench_cnv[:, {
#     'id': f.primid,
#     'belongsToFamily': f.secid,
#     'observedPhenotype': f.Phenotype
# }]

# clinicalDF['observedPhenotype'] = dt.Frame([
#     ','.join(list(set(d.strip().split())))
#     for d in clinicalDF['observedPhenotype'].to_list()[0]
# ])

# clinicalDF['isFetus'] = dt.Frame([
#     'f' in d.lower()
#     for d in clinicalDF['id'].to_list()[0]
# ])

# fetusData = clinicalDF[f.isFetus == True, :].to_pandas().to_dict('records')
# for index,row in enumerate(fetusData):
#     value = row.get('id').strip().replace(' ', '')
    
#     if row['isFetus']:

#         # Pattern 1: 99999F, 99999F1, 99999F1.2
#         pattern1 = re.search(r'((F)|(F[-_])|(F[0-9]{,2})|(F[0-9]{1,2}.[0-9]{1,2}))$', value)
        
#         # Patern 2: 99999F-88888, 99999_88888
#         pattern2 = re.search(r'^([0-9]{1,}(F)?([0-9]{1,2})?[-_=][0-9]{1,})$', value)

#         if pattern1:
#             row['belongsToMother'] = pattern1.string.replace(pattern1.group(0),'')
#             row['validMaternalID'] = row['belongsToMother'] in maternalIDs
#             row['validFamilyID'] = row['belongsToFamily'] in familyIDs
#             row['subjectID'] = pattern1.string
#         elif pattern2:
#             ids = re.split(r'[-_=]', pattern2.string)
#             row['belongsToMother'] = ids[0].replace('F', '')
#             row['validMaternalID'] = row['belongsToMother'] in maternalIDs
#             row['validFamilyID'] = row['belongsToFamily'] in familyIDs
#             row['subjectID'] = ids[0] #.replace('F', '')
#             row['alternativeIdentifiers'] = ids[1]
#         else:
#             status_msg('{}. F detected in {}, but pattern is unexpected'.format(index, value))


# fetusData = pd.DataFrame(fetusData).replace({np.nan:None})
# fetusData = fetusData[[
#     'id',
#     'subjectID',
#     'belongsToFamily',
#     'belongsToMother',
#     'alternativeIdentifiers',
#     'isFetus',
#     'validMaternalID',
#     'validFamilyID'
# ]]

# fetusData['belongsToMother'] = fetusData['belongsToMother'].astype('str')
# fetusData['subjectID'] = fetusData['subjectID'].astype('str')
# fetusData['alternativeIdentifiers'] = fetusData['alternativeIdentifiers'].astype('str')
# fetusData.sort_values(by=['validMaternalID','subjectID']).to_excel('~/Desktop/fetus_data_review.xlsx',index=False)



