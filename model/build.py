#///////////////////////////////////////////////////////////////////////////////
# FILE: build.py
# AUTHOR: David Ruvolo
# CREATED: 2022-11-09
# MODIFIED: 2023-07-05
# PURPOSE: generic build script for EMX models
# STATUS: stable
# PACKAGES: yamlemxconvert
# COMMENTS: NA
#///////////////////////////////////////////////////////////////////////////////

from yamlemxconvert import Convert

# render portal
portal = Convert(files = ['model/cosasportal.yaml'])
portal.convert()
portal.compileSemanticTags()
portal.write(name="cosasportal", outDir="dist")


# render alissa
alissa = Convert(files = ['model/alissa.yaml'])
alissa.convert()
alissa.compileSemanticTags()
alissa.write(name='alissa', outDir='dist')


# report reports
reports = Convert(files = [
  'model/cosasreports.yaml',
  'model/cosasreports_refs.yaml'
])

reports.convert()
reports.compileSemanticTags()
reports.write(name="cosasreports", outDir="dist")