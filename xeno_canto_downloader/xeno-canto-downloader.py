import json
import os
from xenopy import Query

metafiles = 'metafiles'
datasets = 'datasets'

en_names_file = '../shared/en_names.txt'
bird_names_file = '../shared/xeno-canto-names.txt'

missing_recordings_file = 'missing_birds.txt'
ambiguous_names_file = 'ambiguous_names.txt'

missing_recordings = []
ambiguous_bird_names = []
english_bird_names = []


def write_to_file(file_path, data):
    with open(file_path, 'w') as f:
        f.write('\n'.join(data))


try:
    os.mkdir(metafiles)
    os.mkdir(datasets)
except OSError:
    print('Directories already exist, continuing...')

with open(bird_names_file, 'r') as birds:
    bird_names = birds.read().splitlines()

for bird_name in bird_names:

    q = Query(name=bird_name.replace('_', ' '))

    metafile = q.retrieve_meta(verbose=True)
    numRecordings = metafile['numRecordings']

    if numRecordings < 5:
        print(f'Query has too little recordings: {bird_name}')
        missing_recordings.append(bird_name)
        continue

    if int(metafile['numSpecies']) > 1:
        print(f'Query is too ambiguous: {bird_name}')
        ambiguous_bird_names.append(bird_name)
        continue

    continue

    en_name = metafile['recordings'][0]['en'].replace(" ", "")
    english_bird_names.append(en_name)

    filename = f'{metafiles}/{en_name}.json'

    if os.path.isfile(filename):
        print(f'Already existing {filename}')
        continue

    with open(filename, 'w') as json_file:
        json.dump(metafile, json_file)

    q.retrieve_recordings(multiprocess=True, nproc=10, attempts=20, outdir="datasets/")

    print("Download completed.")

write_to_file(missing_recordings_file, missing_recordings)
write_to_file(en_names_file, english_bird_names)
write_to_file(ambiguous_names_file, ambiguous_bird_names)
