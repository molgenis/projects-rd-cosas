#'////////////////////////////////////////////////////////////////////////////
#' FILE: cosas_utils.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-08
#' MODIFIED: 2021-07-08
#' PURPOSE: COSAS tools
#' STATUS: in.progress
#' PACKAGES: *see below*
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////


import molgenis.client as molgenis
import mimetypes
import requests
import json
import yaml
import os
import re
import csv

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


# @title load_config
# @description load yaml configuration file
# @param path path to yaml configuration file
def load_yaml_config(path):
    p = os.path.abspath(path)
    with open(p, 'r') as f:
        d = yaml.safe_load(f)
        f.close()
    return d

# @title load_json
# @description read json file
# @param path location to the file
def load_json(path):
    with open(path, 'r') as file:
        data = json.load(file)
        file.close()
    return data


# @title timestamp
# @description generate a timestamp in H:M:S.ms format
def timestamp():
    return datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]

# @title Status Message
# @description Prints a message with a timestamp
def status_msg(msg):
    print('[' + timestamp() + '] ' + str(msg))