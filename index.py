#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2022-04-06
#' PURPOSE: generate emx files for COSAS
#' STATUS: stable
#' PACKAGES: emxconvert
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from cosas.utils.emxbuildtools import buildEmxTags
import yamlemxconvert
import yaml

# load emx config 
with open('model.yaml', 'r') as stream:
    emxConfig = yaml.safe_load(stream)


# build EMX1 and EMX2 version of each model
for model in emxConfig.get('models'):
    print('Building EMX Model:', model['name'])
    m = yamlemxconvert.Convert(files = model.get('paths'))
    m.convert()
    
    tags = m.tags
    tags.extend(buildEmxTags(m.packages))
    tags.extend(buildEmxTags(m.entities))
    tags.extend(buildEmxTags(m.attributes))
    tags = list({d['identifier']: d for d in tags}.values())
    m.tags = sorted(tags, key = lambda d: d['identifier'])
    
    m.write(model['name'], format='xlsx',outDir=emxConfig['outputPaths'].get('main'))
    m.write_schema(path=f"{emxConfig['outputPaths'].get('schemas')}/{model['name']}_schema.md")
    
    for file in model.get('paths'):
        print('Generating EMX2 version')
        m2 = yamlemxconvert.Convert2(file = file)
        m2.convert()
        m2.write(name=f"{model['name']}_emx2", outDir=emxConfig['outputPaths'].get('main'))
