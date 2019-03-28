#!/usr/bin/python3

import sklearn
import json

dicts_from_file = []

with open('Tweets/20190301:08.out','r') as infile:
    for line in infile.readlines():
        dicts_from_file.append(json.loads(line))

print(dicts_from_file[0]['created_at'])
