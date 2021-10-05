#'////////////////////////////////////////////////////////////////////////////
#' FILE: emx.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-10-05
#' MODIFIED: 2021-10-05
#' PURPOSE: generate emx files for COSAS
#' STATUS: working
#' PACKAGES: emxconvert
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

import sys
from emxconvert.convert import Convert

# get arg if running via the command line
input = sys.argv[1]
print('Selection: {}'.format(input))


# build emx for `cosas` and `cosasrefs`
if input == 'cosas':

    try:
        cosas = Convert(
            files = [
                'emx/src/cosasrefs.yaml',
                'emx/src/cosas.yaml'
            ]
        )

        cosas.convert()
        cosas.write(name = 'cosas', format = 'xlsx', outDir = 'emx/dist/')
        cosas.write_schema(path = 'emx/dist/cosas.md')
        print('Built cosas EMX `emx/dist/cosas.xlsx`')
    except:
        SystemError(
            'Unable to convert emx:\n{}'
            .format(str(sys.exc_info()[0]))
        )

# build emx for `cosasportal`
if input == 'cosasportal':
    try:
        portal = Convert(files = ['emx/src/cosasportal.yaml'])
        portal.convert()
        portal.write(name = 'cosasportal', format = 'xlsx', outDir = 'emx/dist/')
        print('Built cosasportal `emx/dist/cosasportal.xslx`')
    except:
        SystemError(
            'Unable to convert emx:\n{}'
            .format(str(sys.exc_info()[0]))
        )
