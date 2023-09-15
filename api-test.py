import json
import os
from xenopy import Query

q = Query(name='Blue Grosbeak')

metafile = q.retrieve_meta(verbose=True)

print(metafile)