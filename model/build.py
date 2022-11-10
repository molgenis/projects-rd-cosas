#///////////////////////////////////////////////////////////////////////////////
# FILE: build.py
# AUTHOR: David Ruvolo
# CREATED: 2022-11-09
# MODIFIED: 2022-11-09
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

