import numpy as np
import pandas as pd
import json
import re

# Run head -n XXXX first and pipe to a file to use with the below script
# Otherwise, loading 11 gigs of poorly formatted CSV will kill any NF laptop

f = open('C2FO_First_200_Transcripts.csv', 'r')
first200transcripts = re.findall("\[.*\]", f.read())

output = open('first_200_transcripts_reduced.json', 'w')
output.write('{\n')
output.close()

output = open('first_200_transcripts_reduced.json', 'a')
count = 0
transcripts = []
for entry in first200transcripts:
    transcripts.append('"' + str(count) + '"' + ': ' + entry.replace('\\',''))
    count = count + 1
output.write(',\n'.join(transcripts))
output.write('}')
output.close()

with open('first_200_transcripts_reduced.json') as fileToTrim:
    d = json.load(fileToTrim)
    for transcript_key, transcript_value in d.items():
        print (d[transcript_key])
        for transcript_step in d[transcript_key]:
            print(transcript_step)
            del transcript_step['startTime']
            del transcript_step['endTime']
    print(d)    
    with open('first_200_transcripts_reduced.json', 'w') as fileToWrite:
        json.dump(d, fileToWrite)