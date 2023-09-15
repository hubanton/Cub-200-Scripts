import os
import re

# Get the current working directory
current_directory = os.getcwd()


# Specify the folder name and the search string
folder_name = 'datasets'
meta_folder = 'metafiles'

# Create the full path to the 'datasets' folder in the current directory
folder_path = os.path.join(current_directory, folder_name)

matching_files = []
items = os.listdir(folder_path)
metafiles = os.listdir(meta_folder)


matches = []
for item in items:
    for meta in metafiles:
        meta = meta.replace(' ', '')
        if item in meta:
            matches.append(item)
print(len(matches))

residual = []
for match in matches:
    if match != items:
        residual.append(match)

for r in residual:
    print(r)