import json
import os
input_file = 'xeno-canto-names.txt'
metafiles = 'metafiles'

with open(input_file, 'r') as birds:
    bird_names = birds.read().splitlines()


generic_names = []

for bird_name in bird_names:
    filename = f'{metafiles}/{bird_name}.json'
    with open(filename, 'r') as json_file:
        meta_data = json.load(json_file)
        if int(meta_data['numSpecies']) > 1:
            generic_names.append(bird_name)
            os.remove(filename)

with open('generic_names.txt', 'w') as file:
    file.write('\n'.join(generic_names))
