import json
import os
input_file = 'xeno-canto-names.txt'
metafiles = 'metafiles'

directories = os.listdir('datasets')

counts = []
for dir in directories:
    count = len(os.listdir('datasets' + '/' + dir))
    counts.append(count)

counts = sorted(counts)

with open(input_file, 'r') as birds:
    bird_names = birds.read().splitlines()


occurrences = {}

for bird_name in bird_names:
    filename = f'{metafiles}/{bird_name}.json'
    with open(filename, 'r') as json_file:
        meta_data = json.load(json_file)
        num = int(meta_data['numRecordings'])
        occurrences[bird_name] = num

occurrences = dict(sorted(occurrences.items(), key=lambda item: item[1]))

for i, key in enumerate(occurrences):
    if i < 2:
        continue
    if occurrences[key] != counts[i - 2]:
        print(key, occurrences[key], counts[i - 2])