import json
import os
from xenopy import Query

input_file = 'xeno-canto-names.txt'
missing_file = 'missing_birds.txt'
en_names = 'en_names.txt'
metafiles = 'metafiles'
datasets = 'datasets'
missing_recordings = []
en_list = []

if not os.path.exists(metafiles):
    os.mkdir(metafiles)

if not os.path.exists(datasets):
    os.mkdir(datasets)

current_directory = os.getcwd()

with open(input_file, 'r') as birds:
    bird_names = birds.read().splitlines()

for bird_name in bird_names:
    # Search for recordings of the current bird
    q = Query(name=bird_name)

    metafile = q.retrieve_meta(verbose=True)

    if metafile['numRecordings'] == 0:
        print(f'File has no recordings: {bird_name}')
        missing_recordings.append(bird_name)
        continue

    en_name = metafile['recordings'][0]['en'].replace(" ", "")
    en_list.append(en_name)

    filename = f'{metafiles}/{en_name}.json'

    if os.path.isfile(filename):
        print(f'Already existing {filename}')
        continue

    with open(filename, 'w') as json_file:
        en_name = metafile['recordings'][0]['en']
        json.dump(metafile, json_file)

    q.retrieve_recordings(multiprocess=True, nproc=10, attempts=20, outdir="datasets/")


print("Download completed.")

with open(missing_file, 'w') as missing_birds:
    missing_list = '\n'.join(missing_recordings)
    missing_birds.write(missing_list)
    
with open(en_names, 'w') as en_names_file:
    en_names_list = '\n'.join(en_list)
    en_names_file.write(en_names_list)
    
