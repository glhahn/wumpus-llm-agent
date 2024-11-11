#!/usr/bin/env bash

# generate Jupyter notebook in HTML format
jupyter nbconvert --to html --template classic --execute eval-notebook.ipynb
