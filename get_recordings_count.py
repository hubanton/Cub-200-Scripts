import json
import os

input_file = 'xeno-canto-names.txt'
metafiles = 'metafiles'

directories = os.listdir('datasets')

directories = sorted(directories)

counts = {}
for name in directories:
    count = len(os.listdir('datasets' + '/' + name))
    counts[name.split('.')[0]] = count

json.dump(counts, open("num_recordings.json", 'w'), indent=6)
