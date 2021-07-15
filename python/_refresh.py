#'////////////////////////////////////////////////////////////////////////////
#' FILE: _refresh.py
#' AUTHOR: David Ruvolo
#' CREATED: 2021-07-15
#' MODIFIED: 2021-07-15
#' PURPOSE: script for injecting cosastools into designed py files
#' STATUS: in.progress
#' PACKAGES: 
#' COMMENTS: The purpose of this script is to make it easier to reuse the
#'      modules defined in `utils_cosas.py` in other files. Therefore, making
#'      these scripts portable across environments, especially in molgenis.
#'      In this script, define the list of files that should receive the
#'      cosastools modules. In the python files use the following text
#'      anchors:
#'          # @cosastools start
#'          # @cosastools end
#'
#'      Make sure you write code outside of these boundaries!!
#'////////////////////////////////////////////////////////////////////////////

import os

# define files that you would like to manage here
files = ['python/cosas_mapping_initial.py']

# @name read_script
# @description read lines of a python file
# @param path location of the py file to load
# @return a list of lines
def read_script(path):
    with open(file = os.path.abspath(path), mode = 'r') as file:
        script = file.readlines()
    file.close()
    return script

# @name write_script
# @description save lines into a py script
# @param path output location of the file
# @param x list containing lines to write
# @return None
def write_script(path, x):
    with open(file = os.path.abspath(path), mode = 'w', encoding = 'utf-8') as file:
        for line in x:
            file.write(line)
    file.close()
    return None

# @name list_index_all
# @description return the indices of all matching values
# @param x a list to search through
# @param value value to use to find indices
# @return a list of indices
def list_index_all(x, value): 
    return [i for i, d in enumerate(x) if d == value]

#//////////////////////////////////////

# load cosastools
cosastools = read_script(path = 'python/utils_cosas.py')

# remove headers from cosastools script
cosastools_trimmed = cosastools[cosastools.index("# @cosastools start\n")+1:cosastools.index("# @cosastools end\n")]

# insert cosastools into all files
for f in files:
    contents = read_script(path = f)
    start = contents[0:contents.index('# @cosastools start\n')+1]
    end = contents[contents.index('# @cosastools end\n'):len(contents)]
    new = start + cosastools_trimmed + end
    write_script(path = f, x = new)
    





