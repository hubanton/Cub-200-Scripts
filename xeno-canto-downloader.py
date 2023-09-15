import json
import os
from xenopy import Query

input_file = 'xeno-canto-names.txt'
missing_file = 'missing_birds.txt'
metafiles = 'metafiles'
datasets = 'datasets'
missing_recordings = []


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

    filename = f'{metafiles}/{bird_name}.json'

    print(filename)

    if os.path.isfile(filename):
        print('Already existing')
        continue
    else:
        print(f'Downloading {bird_name}')
    metafile = q.retrieve_meta(verbose=True)

    with open(filename, 'w') as json_file:
        json.dump(metafile, json_file)

    if metafile['numRecordings'] != 0:
        # Get the first recording (you can customize this)
        q.retrieve_recordings(multiprocess=True, nproc=10, attempts=10, outdir="datasets/")

        print(f"Downloaded: {bird_name}")
    else:
        missing_recordings.append(bird_name)
        print(f"No recordings found for: {bird_name}")

print("Download completed.")

with open(missing_file, 'w') as missing_birds:
    missing_list = '\n'.join(missing_recordings)
    missing_birds.write(missing_list)
