#'////////////////////////////////////////////////////////////////////////////
#' FILE: emxbuildtools.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-02-14
#' MODIFIED: 2022-06-29
#' PURPOSE: utils for building emx files
#' STATUS: stable
#' PACKAGES: NA
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

def buildEmxTags(data: list=[]):
    """Build Emx Tags
    Collate all tags defined in the `tags` property and transform into EMX
    format.
    
    @param data (list) : converted emx object (packages, entities, attributes)
    
    @return record set
    """
    rawTags=list(set([row['tags'] for row in data if 'tags' in row]))
    tagsToProcess=[
        {'label': tag.split(' ')[0], 'iri': tag.split(' ')[1]}
        for tag in rawTags
    ]

    builtTags=[]
    for tag in tagsToProcess:
        builtTags.append({
            'identifier': tag['label'],
            'label': tag['label'],
            'objectIRI': tag['iri'],
            'codeSystem': tag['label'].split('_')[0],
            'relationLabel': 'isAssociatedWith',
            'relationIRI': 'http://molgenis.org#isAssociatedWith'
        })
        
    return builtTags


def extractTagId(data: list=[]):
    """Extract Tag Identifier
    @param data input dataset from yamlemxconvert.convert (packages, entities, etc.)
    """
    for row in data:
        if row.get('tags'):
            row['tags']=row['tags'].split(' ')[0]