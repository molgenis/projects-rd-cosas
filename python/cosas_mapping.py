#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_mapping.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-15
#' MODIFIED: 2021-07-15
#' PURPOSE: primary COSAS mapping script
#' STATUS: in.progress
#' PACKAGES: *see below*
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import pandas as pd

# @cosastools start
import molgenis.client as molgenis
import mimetypes
import requests
import json
import os

from urllib.parse import quote_plus
from datetime import datetime

# @title molgenis
# @description extend molgenis class
class molgenis(molgenis.Session):
    # @title Update Table
    # @name update_table
    # @description batch update a molgenis entity
    # @param self required class param
    # @param data object containing data to import
    # @param entity ID of the target entity written as 'package_entity'
    # @return a response code
    def update_table(self, data, entity):
        if len(data) < 1000:
            response = self._session.post(
                url = self._url + 'v2/' + quote_plus(entity),
                headers = self._get_token_header_with_content_type(),
                data = json.dumps({'entities' : data})
            )
            if response.status_code == 201:
                status_msg(
                    'Successfully imported data (response: {})'
                    .format(response.status_code)
                )
            else:
                status_msg(
                    'Failed to import data (response: {}): \nReason:{}'
                    .format(response.status_code, response.content)
                )
        else:    
            for d in range(0, len(data), 1000):
                response = self._session.post(
                    url=self._url + 'v2/' + entity,
                    headers=self._get_token_header_with_content_type(),
                    data=json.dumps({'entities': data[d:d+1000]})
                )
                if response.status_code == 201:
                    status_msg(
                        'Successfuly imported batch {} (response: {})'
                        .format(d, response.status_code)
                    )
                else:
                    status_msg(
                        'Failed to import data (response: {}): \nReason:{}'
                        .format(response.status_code, response.content)
                    )
    # @title Batch Update Entity Attribute
    # @name batch_update_one_attr
    # @description import data for an attribute in groups of 1000
    # @param self required class param
    # @param entity ID of the target entity written as `package_entity`
    # @param values data to import, a list of dictionaries where each dictionary
    #       is structured with two keys: the ID attribute and the attribute
    #       that you wish to update. E.g. [{'id': 'id123", 'x': 1},...]
    # @return a response code
    def batch_update_one_attr(self, entity, attr, values):
        add = 'No new data'
        for i in range(0, len(values), 1000):
            add = 'Update did tot go OK'
            """Updates one attribute of a given entity with the given values of the given ids"""
            response = self._session.put(
                self._url + "v2/" + quote_plus(entity) + "/" + attr,
                headers=self._get_token_header_with_content_type(),
                data=json.dumps({'entities': values[i:i+1000]})
            )
            if response.status_code == 200:
                add = 'Update went OK'
            else:
                try:
                    response.raise_for_status()
                except requests.RequestException as ex:
                    self._raise_exception(ex)
                return response
        return add
    # @title Batch Remove Data
    # @name batch_remove
    # @description remove data from an entity using a list of row IDs
    # @param selef required param
    # @param entity ID of the target entity written as `package_entity`
    # @param data a list row IDs (must contain values of the idAttribute)
    # @return a response code
    def batch_remove(self, entity, data):
        if len(data) < 1000:
            self.delete_list(entity = entity, entities = data)
        else:
            for d in range(0, len(data), 1000):
                self.delete_list(
                    entity = entity,
                    entities = data[d+d:1000]
                )
    # @title Upload File
    # @name upload_file
    # @description upload file (pdf, word, etc.) into Molgenis
    # @param self required molgenis param
    # @param name name of the file to use in Molgenis
    # @param path location to the file
    # @return a response code
    def upload_file(self, name, path):
        filepath = os.path.abspath(path)
        url = self._url + 'files/'
        header = {
            'x-molgenis-token': self._token,
            'x-molgenis-filename': name,
            'Content-Length': str(os.path.getsize(filepath)),
            'Content-Type': str(mimetypes.guess_type(filepath)[0])
        }
        with open(filepath,'rb') as f:
            data = f.read()
        f.close()
        response = requests.post(url, headers=header, data=data)
        if response.status_code == 201:
            print(
                'Successfully imported file:\nFile Name: {}\nFile ID: {}'
                .format(
                    response.json()['id'],
                    response.json()['filename']
                )
            )
        else:
            response.raise_for_status()


# @title Add Forward Slash
# @name __add_forward_slash
# @description Adds forward slash to the end of a path if missing
# @param path a string containing a path to a given location (file, url, etc.)
# @returns a string
def __add__forward__slash(path):
    return path + '/' if path[len(path)-1] != '/' else path


# @title Extract Nested Attribute
# @description extract attribute from nested dictionary
# @param data input dataset a list of dictionaries
# @param attr value to extract
# @return a string of values
def attr_extract_nested(data, attr):
    value = None
    if len(data) == 1:
        value = data[0].get(attr)
    if len(data) > 1:
        joined_att = []
        for d in data:
            joined_att.append(d.get(attr))
        value = ','.join(map(str, joined_att))
    return value


# @title flatten attribute
# @description pull values from a specific attribute
# @param data list of dict
# @param name of attribute to flatten
# @param distinct if TRUE, return unique cases only
# @return a list of values
def attr_flatten(data, attr, distinct=False):
    out = []
    for d in data:
        tmp_attr = d.get(attr)
        out.append(tmp_attr)
    if distinct:
        return list(set(out))
    else:
        return out

# @title distinct
# @description get distinct dictionnaires only
# @param data a list containing one or more dictionaries 
# @param key one or more keys to filter by
# @examples
# dict_distinct(data, lambda x: ( x['id'], x['experimentID'] )))
# @return a list containing distinct dictionaries
def dict_distinct(data, key):
    if key is None:
        key = lambda x: x
    seen = set()
    for d in data:
        k = key(d)
        if k in seen:
            continue
        yield d
        seen.add(k)
    return seen

# @title Unique Dictionaries
# @description get unique dictionaries based on values of a named key
# @param data list of dictionaries to filter
# @param key attribute to used to filter
# @return a list of dictionaries filtered
def dict_unique(data, key):
    return [dict(key) for key in set(tuple(x.items()) for x in data)]

# @title filter list of dictionaries
# @param data object to search
# @param attr variable find match
# @param value value to filter for
# @return a list of a dictionary
def dict_filter(data, attr, value):
    return list(filter(lambda d: d[attr] in value, data))


# @title select keys
# @describe reduce list of dictionaries to named keys
# @param data list of dictionaries to select
# @param keys an array of values
# @return a list of dictionaries
def dict_select(data, keys):
    return list(map(lambda x: {k: v for k, v in x.items() if k in keys}, data))

# @title timestamp
# @description generate a timestamp in H:M:S.ms format
def timestamp():
    return datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]

# @title Status Message
# @description Prints a message with a timestamp
def status_msg(msg):
    print('[' + timestamp() + '] ' + str(msg))

# @cosastools end

# @title read_xlsx
# @description read xlsx file and return as list of dictionaries
# @param path location of the file to read
# @param nrows number of rows to read
# @param converters dictionary containing attribute-data type mappings
# @return a list of dictionaries
def read_xlsx(path, nrows = None, converters = None):
    data = pd.read_excel(
        path,
        engine = 'openpyxl',
        nrows = nrows,
        converters = converters,
        dtype = str
    )
    return data.to_dict('records')

# @title Map COSAS patients
# @name map_cosas_patients
# @description Map portal table into COSAS patients terminology
# @param data an object you wish to map into cosas_patients
# @return a list of dictionaries
def map_cosas_patients(data):
    # f = "%d/%m/%Y"
    f = "%Y-%m-%d %H:%M:%S"
    out = []
    for d in data:
        tmp = {
            'umcg_numr': d.get('UMCG_nummer'),
            'family_numr': d.get('Familienummer'),
            'dob': d.get('Geboortedatum'),
            'biological_sex': d.get('Geslacht').lower(),
            'maternal_id': d.get('UMCG_moeder'),
            'paternal_id': d.get('UMCG_vader'),
            'linked_family_ids': d.get('Familieleden').replace(' ', ''),
            'is_deceased': 'nee',
            'date_deceased': d.get('Overlijdensdatum'),
            'date_first_consult': None
        }
        # reformat dates and update applicable status variables
        if tmp['dob'] or tmp['dob'] != '':
            tmp['dob'] = datetime.strptime(tmp['dob'], f).date()
        if 'date_deceased' in tmp:
            if not str(tmp['date_deceased']) == 'nan':
                tmp['date_deceased'] = datetime.strptime(tmp['date_deceased'], f).date()
                tmp['is_deceased'] = 'ja'
        out.append(tmp)
    return out

# @title Recode Diagnostic Codes
# @name __recode__dx__code
def __recode__dx__code(x, attr):
    if x[attr]:
        if ':' in x[attr]:
            x[attr] = 'dx_' + x[attr].split(':')[0]
        else:
            x[attr] = None
    else:
        x[attr] = None

# @title Recode Diagnostic Certainty
# @name __recode__dx__certainty
# @description standardize diagnostic certainty values
# @param x dictionary containing diagnostic certainty attribute
# @param attr the name of the diagnostic certainty attribute
# @return recoded dictionary
def __recode__dx__certainty(x, attr):
    if x[attr]:
        if x[attr] != '' or x[attr] != '-':
            x[attr] = x[attr].lower().replace(' ', '-')
    else:
        x[attr] = None

# @title MAP COSAS Diagnoses
# @name map_cosas_diagnoses
# @description Map portal table into COSAS terminology
# @param data an object you wish to map
# @return a list of dictionaries
def map_cosas_diagnoses(data):
    # f = "%d/%m/%Y"
    f = "%Y-%m-%d %H:%M:%S"
    out = []
    for d in data:
        tmp = {
            'umcg_numr': d.get('UMCG_NUMBER'),
            'primary_dx': d.get('HOOFDDIAGNOSE'),
            'primary_dx_certainty': d.get('HOOFDDIAGNOSE_ZEKERHEID'),
            'extra_dx': d.get('EXTRADIAGNOSE'),
            'extra_dx_certainty': d.get('EXTRADIAGNOSE_ZEKERHEID'),
            'ond_id': d.get('OND_ID'),
            'date_first_consult': d.get('DATUM_EERSTE_CONSULT')
        }
        # recode values and format date of first consult
        __recode__dx__code(tmp, 'primary_dx')
        __recode__dx__code(tmp, 'extra_dx')
        __recode__dx__certainty(tmp, 'primary_dx_certainty')
        __recode__dx__certainty(tmp, 'extra_dx_certainty')
        if str(tmp['date_first_consult']) != 'nan':
            tmp['date_first_consult'] = datetime.strptime(
                str(tmp['date_first_consult']), f
            ).date()
        out.append(tmp)
    return out


# @title Find date of first consult
# @name calc__first__date
# @description Given a long format dataset and an ID, what is the earliest date?
# @param data a list of dictionaries
# @param id name of the ID attribute
# @param date the name of the date attribute
# @return a list of IDs and attributes
def calc__first__date(data, id, date):
    ids = attr_flatten(data = data, attr = id)
    out = []
    for i in ids:
        results = dict_filter(data = data, attr = id, value = i)
        dates = attr_flatten(data = results, attr = date)
        dates = [d for d in dates if str(d) != 'nan']
        if dates:
            tmp = {}
            tmp[id] = str(i)
            tmp[date] = min(dates)
            out.append(tmp)
    return out


# @title Merge first date consult data with patients
# @name merge__patient__dates
# @param patients object containing patient metadata
# @param dates object containing dates per ID
# @return the patients object with dates added where applicable
def merge__patient__dates(patients, dates):
    for p in patients:
        results = dict_filter(data = dates, attr = 'umcg_numr', value = p['umcg_numr'])
        if results:
            p['date_first_consult'] = results[0].get('date_first_consult')




#'/////////////////////////////////////////////////////////////////////////////

# define flags
should = {
    'map': {
        'cosas_patients_date_first_consult': False
    },
    'push': {
        'cosas_patients': False,
        'cosas_diagnoses': False,
        'cosas_samples': False,
        'cosas_labs_array': False,
        'cosas_labs_ngs': False,
    },
    'update': {
        'cosas_patients_date_first_consult': False
    }
}

status_msg("Starting COSAS mapping! :-)")

# init session
host = "https://cosas-acc.gcc.rug.nl/api/"
token = '${molgenisToken}'
cosas = molgenis(url = host, token = token)

# pull all portal data
status_msg('Pulling data from portal...')

cosas_patients = cosas.get(entity = 'cosas_patients', batch_size = 10000)
# cosas_patient_ids = attr_flatten(
#     data = cosas_patients,
#     attr = 'umcg_numr',
#     distinct = True
# )

# portal_patients = cosas.get(
#     entity = 'cosasportal_patients',
#     q = 'processed=="false"',
#     batch_size = 10000
# )

# portal_diagnoses = cosas.get(
#     entity = 'cosasportal_diagnoses',
#     q = 'processed=="false"',
#     batch_size = 10000
# )

# bench_cnv = cosas.get(
#     entity = 'cosasportal_bench_cnv',
#     q = 'processed=="false"',
#     batch_size = 10000
# )

# DEV ONLY - simulate initial upload only
cosas_patient_ids = []
portal_patients = read_xlsx(
    path = 'data/cosasportal/cosasportal_patients.xlsx',
    nrows = 500
)

portal_diagnoses = read_xlsx(
    path = 'data/cosasportal/cosasportal_diagnoses.xlsx',
    nrows = 500
)

# bench_cnv = read_xlsx(
#     path = 'data/cosasportal/cosasportal_bench_cnv.xlsx'
# )

# map `cosasportal_patients`
should_map_consult_dates = False
if portal_patients:
    status_msg('Mapping patient portal table...')
    portal_patients_mapped = map_cosas_patients(data = portal_patients)
    #
    # update flag that indicates consult date data should be merged
    #
    if portal_patients_mapped:
        should['push']['cosas_patients'] = True
        should['map']['cosas_patients_date_first_consult'] = True
        status_msg(
            "Mapped patients (NROW: {})"
            .format(len(portal_patients_mapped))
        )
else:
    status_msg('Data in `cosasportal_patients` is already processed :-p')

# map `cosasportal_diagnoses`
if portal_diagnoses:
    status_msg('Mapping diagnoses table...')
    portal_diagnoses_mapped = map_cosas_diagnoses(data = portal_diagnoses)
    status_msg(
        "Mapped diagnoses (NROW: {})"
        .format(len(portal_diagnoses_mapped))
    )
    # find the date of first consult and merge with patients metadat
    portal_patients_visit_dates = calc__first__date(
        data = portal_diagnoses_mapped,
        id = 'umcg_numr',
        date = 'date_first_consult'
    )
    # should the we join with `cosasportal_patients`?
    if should['map']['cosas_patients_date_first_consult']:
        status_msg('Merging consult date data with patients...')
        merge__patient__dates(
            patients = portal_patients_mapped,
            dates = portal_patients_visit_dates
        )
    else:
        # otherwise, attempt to locate cases to update
        status_msg('No patient data available to merge. Attempting to locate potential updates')
        if cosas_patient_ids:
            status_msg('Finding cases to update')
            cosas_patients_visit_dates = []
            for d in portal_patients_visit_dates:
                result = dict_filter(
                    data = cosas_patients,
                    attr = 'umcg_numr',
                    value = d['umcg_numr']
                )
                if result:
                    d['id'] = result[0].get('id')
                    cosas_patients_visit_dates.append(d)
            if cosas_patients_visit_dates:
                status_msg(
                    'Rows to update {}'
                    .format(len(cosas_patients_visit_dates))
                )
                should['update']['cosas_patients_date_first_consult']
            else:
                status_msg('No consult dates to update')
        else:
            status_msg('No IDs exist. Unable to run updates')
else:
    status_msg("Data in `cosasportal_diagnoses` is already processed. :-)")

#'/////////////////////////////////////

# upload data
status_msg('Pushing data...')

# push to `cosas_patients`
if should['push']['cosas_patients']:
    status_msg('Pushing new data to cosas_patients')
    cosas.update_table(
        data = portal_patients_mapped,
        entity = 'cosas_patients'
    )

# update `date_firsts_consult` in `cosas_patients`
if should['update']['cosas_patients_date_first_consult']:
    status_msg('Updating consult date data')
    cosas_patients_date_first_consult_updates = dict_select(
        data = cosas_patients_visit_dates,
        keys = ['id', 'date_first_consult']
    )
    cosas.batch_update_one_attr(
        entity = 'cosas_patients',
        attr = 'date_first_consult',
        values = cosas_patients_date_first_consult_updates
    )

# triage portal data
# status_msg('Triaging portal data...')
# portal_patients_new = []
# portal_patients_updates = []
# for p in portal_patients_mapped:
#     if cosas_patient_ids:
#         if p['UMCG_nummer'] in cosas_patient_ids:
#             portal_patients_updates.append(p)
#         else:
#             portal_patients_new.append(p)
#     else:
#         portal_patients_new.append(p)

# status_msg(
#     'Triage results:\n\t- New: {}\n\t- Updates:{}'
#     .format(len(portal_patients_new), len(portal_patients_updates))
# )
