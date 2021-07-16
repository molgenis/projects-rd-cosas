#!/bin/bash

# define files to copy
declare -a files=("emx/cosas/cosas.xlsx" "emx/cosas-portal/cosasportal.xlsx" "emx/cosas-refs/cosasrefs.xlsx")

# copy files
for f in "${files[@]}"; do
    echo "Copying: ${f}"
    cp "$f" ~/Documents/OneDrive\ -\ UMCG/projects/cosas/emx/
done