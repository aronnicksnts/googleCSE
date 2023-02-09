import json
import math
from googleapiclient.discovery import build

dataJSON = json.load(open('data.json'))

def getImages(query: str, totalNumImages: int):
    totalNumImages = math.ceil(totalNumImages/10)
    service = build("customsearch", 'v1', developerKey=dataJSON['customSearchAPI'])
    allResponses = []

    for i in range(totalNumImages):
        response = service.cse().list(
            q=query,
            cx=dataJSON['searchEngineID'],
            searchType='image',
            num=10,
            imgType='photo',
            safe= 'off',
            start=10*i+1
        ).execute()
        allResponses.append(response)

    if not allResponses:
        return None
    else:
        return allResponses

test = getImages("hello", 22)
print(f'Size of allResponses: {len(test)}\nSize of inside: {len(test[0])}')