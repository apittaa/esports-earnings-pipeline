import json

# Read JSON file
with open('credentials/esports-earnings-pipeline-google-credentials.json', 'r') as data:
    data = json.load(data)

# Convert JSON data to string
print(json.dumps(data))
