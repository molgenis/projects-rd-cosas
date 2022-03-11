#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2022-02-23
#' PURPOSE: generate emx files for COSAS
#' STATUS: working
#' PACKAGES: emxconvert
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from yamlemxconvert import Convert, Convert2
from python.utils_emx import buildEmxTags

# render umdm portal
cosas = Convert(files = ['model/cosasportal.yaml', 'model/cosasportal_mappings.yaml'])
cosas.convert()
cosas.write('cosasportal', format='xlsx', outDir='dist')
cosas.write_schema(path = 'dist/schema_cosasportal.md')


# render reports emx
reports = Convert(files = ['model/cosasreports.yaml', 'model/cosasreports_refs.yaml'])
reports.convert()

# build tags
tags = reports.tags
tags.extend(buildEmxTags(reports.packages))
tags.extend(buildEmxTags(reports.entities))
tags.extend(buildEmxTags(reports.attributes))
tags = list({d['identifier']: d for d in tags}.values())
reports.tags = sorted(tags, key = lambda d: d['identifier'])

# write
reports.write('cosasreports', format='xlsx', outDir='dist')
reports.write_schema(path='dist/schema_cosasreports.md')

# Optional EMX2
cosas2 = Convert2(file='model/cosasportal.yaml')
cosas2.convert()
cosas2.write(name='cosasportal_emx2', outDir='dist')