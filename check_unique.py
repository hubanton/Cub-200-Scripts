import json
import os
input_file = 'en_names.txt'
metafiles = 'metafiles'

with open(input_file, 'r') as birds:
    bird_names = birds.read().splitlines()

    unique = set(bird_names)

    print(len(unique), len(bird_names))

for item in unique:
    count = bird_names.count(item)
    if count == 2:
        print(item)