#'////////////////////////////////////////////////////////////////////////////
#' FILE: gh_download_files.py
#' AUTHOR: David Ruvolo
#' CREATED: 2022-05-05
#' MODIFIED: 2022-05-05
#' PURPOSE: download files from github repo
#' STATUS: stable
#' PACKAGES: cosas.api.github
#' COMMENTS: NA
#'////////////////////////////////////////////////////////////////////////////

from cosas.api.github import github


# download files from apps/helloworld
gh=github(owner='molgenis', repo="molgenis-emx2")

files=gh.listContents(path="apps/helloworld")

for file in files[:1]:
    print('Downloading file',file['name'],'....')
    contents=gh.GET(file['url'], stream=True)
    with open(f"app/cosas-emx2/{file['name']}", 'wb') as f:
        f.write(contents)